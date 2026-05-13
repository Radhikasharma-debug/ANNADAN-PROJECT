"""
Route Optimization
Optimize delivery routes for efficient food distribution
"""

from app.ai.utils import LocationUtils


class RouteOptimizer:
    """Optimize delivery routes for NGOs"""

    def __init__(self, db):
        self.db = db
        self.ngos_collection = db.ngos
        self.donations_collection = db.donations
        self.deliveries_collection = self._resolve_deliveries_collection(db)

    def optimize_route(self, ngo_id, pickup_locations, delivery_locations, vehicle_capacity=100):
        """
        Optimize route for food delivery
        Uses nearest neighbor heuristic and 2-opt improvements
        """
        try:
            # Get NGO base location
            ngo = self.ngos_collection.find_one({'_id': ngo_id})
            if not ngo:
                return {'success': False, 'error': 'NGO not found'}

            ngo_location = ngo.get('location', {})
            ngo_lat, ngo_lon = self._extract_coordinates(ngo_location)

            # Prepare locations with coordinates
            all_locations = [
                {
                    'id': 'warehouse',
                    'type': 'warehouse',
                    'latitude': ngo_lat,
                    'longitude': ngo_lon,
                    'location_name': ngo_location.get('address', 'NGO Warehouse'),
                    'quantity': 0.0,
                    'seq': 0,
                }
            ]

            # Pickup locations
            for idx, location in enumerate(pickup_locations or []):
                latitude, longitude = self._extract_coordinates(location)
                all_locations.append(
                    {
                        'id': f'pickup_{idx}',
                        'type': 'pickup',
                        'latitude': latitude,
                        'longitude': longitude,
                        'location_name': location.get('address', f'Pickup {idx + 1}'),
                        'quantity': self._to_number(location.get('quantity', 0)),
                        'seq': idx + 1,
                    }
                )

            # Delivery locations
            for idx, location in enumerate(delivery_locations or []):
                latitude, longitude = self._extract_coordinates(location)
                all_locations.append(
                    {
                        'id': f'delivery_{idx}',
                        'type': 'delivery',
                        'latitude': latitude,
                        'longitude': longitude,
                        'location_name': location.get('address', f'Delivery {idx + 1}'),
                        'quantity': self._to_number(location.get('quantity', 0)),
                        'seq': len(pickup_locations or []) + idx + 2,
                    }
                )

            if len(all_locations) <= 1:
                return {'success': False, 'error': 'At least one pickup or delivery location is required'}

            # Calculate distance matrix
            distance_matrix = self._calculate_distance_matrix(all_locations)

            # Optimize route order
            optimized_route = self._optimize_tsm(
                distance_matrix=distance_matrix,
                start_idx=0,  # Start from warehouse
            )

            # Calculate route details
            route_details = self._calculate_route_details(
                optimized_route=optimized_route,
                locations=all_locations,
                distance_matrix=distance_matrix,
                vehicle_capacity=max(1.0, self._to_number(vehicle_capacity, default=100)),
            )

            return {
                'success': True,
                'ngo_id': str(ngo_id),
                'optimized_route': route_details['route'],
                'total_distance_km': round(route_details['total_distance'], 2),
                'total_time_minutes': round(route_details['total_time'], 0),
                'stops': route_details['stops'],
                'efficiency_score': round(route_details['efficiency_score'], 2),
                'vehicle_capacity_used': round(route_details['capacity_used_percent'], 1),
                'co2_saved_kg': round(route_details['co2_saved'], 2),
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def optimize_multi_vehicle_route(self, ngo_id, locations, num_vehicles=2, vehicle_capacity=100):
        """
        Optimize routes for multiple vehicles
        Useful for NGOs with multiple delivery personnel
        """
        try:
            ngo = self.ngos_collection.find_one({'_id': ngo_id})
            if not ngo:
                return {'success': False, 'error': 'NGO not found'}

            num_vehicles = max(1, int(num_vehicles or 1))

            # Separate pickups and deliveries
            pickups = [loc for loc in (locations or []) if loc.get('type') == 'pickup']
            deliveries = [loc for loc in (locations or []) if loc.get('type') == 'delivery']

            # Cluster deliveries by location to balance vehicle loads
            clusters = self._cluster_locations(deliveries, num_vehicles)

            optimized_routes = []
            total_distance = 0.0
            total_time = 0.0

            for cluster_idx, cluster_locations in enumerate(clusters):
                route_result = self.optimize_route(
                    ngo_id=ngo_id,
                    pickup_locations=pickups,
                    delivery_locations=cluster_locations,
                    vehicle_capacity=vehicle_capacity,
                )

                if route_result.get('success'):
                    optimized_routes.append(
                        {
                            'vehicle_id': f'vehicle_{cluster_idx + 1}',
                            'route': route_result['optimized_route'],
                            'distance_km': route_result['total_distance_km'],
                            'time_minutes': route_result['total_time_minutes'],
                            'stops': route_result['stops'],
                            'capacity_used': route_result['vehicle_capacity_used'],
                        }
                    )

                    total_distance += float(route_result['total_distance_km'])
                    total_time += float(route_result['total_time_minutes'])

            return {
                'success': True,
                'ngo_id': str(ngo_id),
                'num_vehicles': num_vehicles,
                'routes': optimized_routes,
                'total_distance_km': round(total_distance, 2),
                'total_time_minutes': round(total_time, 0),
                'average_efficiency': round(total_distance / max(1, num_vehicles), 2),
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_realtime_tracking(self, delivery_id):
        """Get realtime location and status of ongoing delivery"""
        try:
            delivery = self.deliveries_collection.find_one({'_id': delivery_id})
            if not delivery:
                return {'success': False, 'error': 'Delivery not found'}

            return {
                'success': True,
                'delivery_id': str(delivery_id),
                'status': delivery.get('status', 'pending'),
                'current_location': delivery.get('current_location'),
                'next_stop': delivery.get('next_stop'),
                'stops_completed': delivery.get('stops_completed', 0),
                'total_stops': delivery.get('total_stops', 0),
                'estimated_completion_time': delivery.get('eta'),
                'distance_remaining_km': delivery.get('distance_remaining'),
                'vehicle_id': delivery.get('vehicle_id'),
                'driver_name': delivery.get('driver_name'),
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def suggest_consolidation(self, ngo_id):
        """Suggest delivery consolidation opportunities"""
        try:
            # accepted_by stores NGO user_id in donor/ngo routes; support both ids.
            accepted_by_values = [str(ngo_id)]
            ngo = self.ngos_collection.find_one({'_id': ngo_id})
            if ngo and ngo.get('user_id'):
                accepted_by_values.append(str(ngo.get('user_id')))

            pending_cursor = self.donations_collection.find(
                {
                    'accepted_by': {'$in': accepted_by_values},
                    'status': 'accepted',
                }
            )
            pending_deliveries = self._limit_results(pending_cursor, 20)

            if len(pending_deliveries) < 2:
                return {
                    'success': True,
                    'message': 'Not enough pending deliveries to consolidate',
                    'consolidation_opportunities': [],
                    'total_distance_savings_km': 0,
                    'total_co2_savings_kg': 0,
                }

            # Find deliveries to same location
            location_groups = {}
            for delivery in pending_deliveries:
                location = delivery.get('location', {}).get('address', '')
                if location:
                    location_groups.setdefault(location, []).append(delivery)

            recommendations = []
            total_savings = 0.0

            for location, deliveries in location_groups.items():
                if len(deliveries) > 1:
                    # Calculate potential savings (simple heuristic)
                    trips_saved = len(deliveries) - 1
                    distance_saved = trips_saved * 5.0  # assumed 5km per trip
                    time_saved = trips_saved * 15.0  # assumed 15 min per trip

                    recommendations.append(
                        {
                            'location': location,
                            'consolidation_count': len(deliveries),
                            'trips_saved': trips_saved,
                            'distance_saved_km': distance_saved,
                            'time_saved_minutes': time_saved,
                            'co2_saved_kg': distance_saved * 0.21,  # 0.21 kg CO2 per km
                        }
                    )

                    total_savings += distance_saved

            return {
                'success': True,
                'consolidation_opportunities': recommendations,
                'total_distance_savings_km': total_savings,
                'total_co2_savings_kg': round(total_savings * 0.21, 2),
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_optimization_stats(self, ngo_id):
        """Get statistics on route optimization"""
        try:
            ngo_id_str = str(ngo_id)

            completed = self._count_documents(
                self.deliveries_collection,
                {
                    'ngo_id': ngo_id_str,
                    'status': 'completed',
                },
            )

            # Use aggregation when supported
            if hasattr(self.deliveries_collection, 'aggregate'):
                pipeline = [
                    {'$match': {'ngo_id': ngo_id_str, 'status': 'completed'}},
                    {
                        '$group': {
                            '_id': None,
                            'avg_distance': {'$avg': '$distance_km'},
                            'avg_time': {'$avg': '$time_minutes'},
                            'avg_stops': {'$avg': '$stops'},
                        }
                    },
                ]

                result = list(self.deliveries_collection.aggregate(pipeline))
                if result:
                    stats = result[0]
                    return {
                        'success': True,
                        'completed_deliveries': completed,
                        'average_distance_km': round(stats.get('avg_distance', 0) or 0, 2),
                        'average_time_minutes': round(stats.get('avg_time', 0) or 0, 0),
                        'average_stops_per_route': round(stats.get('avg_stops', 0) or 0, 1),
                    }

            # Fallback for mock DB
            completed_deliveries = self._find_documents(
                self.deliveries_collection,
                {
                    'ngo_id': ngo_id_str,
                    'status': 'completed',
                },
            )

            if completed_deliveries:
                avg_distance = sum(self._to_number(d.get('distance_km', 0)) for d in completed_deliveries) / len(
                    completed_deliveries
                )
                avg_time = sum(self._to_number(d.get('time_minutes', 0)) for d in completed_deliveries) / len(
                    completed_deliveries
                )
                avg_stops = sum(self._to_number(d.get('stops', 0)) for d in completed_deliveries) / len(
                    completed_deliveries
                )

                return {
                    'success': True,
                    'completed_deliveries': completed,
                    'average_distance_km': round(avg_distance, 2),
                    'average_time_minutes': round(avg_time, 0),
                    'average_stops_per_route': round(avg_stops, 1),
                }

            return {
                'success': True,
                'completed_deliveries': 0,
                'message': 'No completed deliveries yet',
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _resolve_deliveries_collection(self, db):
        """Support both real Mongo DB and mock DB collection access patterns."""
        try:
            return db.get_collection('deliveries')
        except Exception:
            try:
                return db.deliveries
            except Exception:
                return db['deliveries']

    def _extract_coordinates(self, location):
        """Extract coordinates from various location payload formats."""
        if not isinstance(location, dict):
            return 0.0, 0.0

        # Mongo geo style: [longitude, latitude]
        coordinates = location.get('coordinates')
        if isinstance(coordinates, (list, tuple)) and len(coordinates) >= 2:
            return self._to_number(coordinates[1]), self._to_number(coordinates[0])

        latitude = location.get('latitude')
        longitude = location.get('longitude')
        if latitude not in (None, '') and longitude not in (None, ''):
            return self._to_number(latitude), self._to_number(longitude)

        # Fallback geocoding by address (utility currently uses mock city map)
        address = location.get('address')
        if address:
            geo_lat, geo_lon = LocationUtils.get_location_from_address(address)
            return self._to_number(geo_lat), self._to_number(geo_lon)

        return 0.0, 0.0

    def _calculate_distance_matrix(self, locations):
        """Calculate distance matrix between all locations"""
        n = len(locations)
        matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = LocationUtils.haversine_distance(
                        locations[i]['latitude'],
                        locations[i]['longitude'],
                        locations[j]['latitude'],
                        locations[j]['longitude'],
                    )
                    matrix[i][j] = dist

        return matrix

    def _optimize_tsm(self, distance_matrix, start_idx=0, max_iterations=100):
        """
        Solve Traveling Salesman Problem using nearest neighbor + 2-opt
        Returns optimized order of location indices
        """
        n = len(distance_matrix)

        # Nearest neighbor heuristic
        unvisited = set(range(n))
        current = start_idx
        route = [current]
        unvisited.remove(current)

        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest

        # Return to start
        route.append(start_idx)

        # 2-opt improvement
        improved = True
        iterations = 0

        while improved and iterations < max_iterations:
            improved = False
            iterations += 1

            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route) - 1):
                    old_dist = distance_matrix[route[i - 1]][route[i]] + distance_matrix[route[j]][route[j + 1]]
                    new_dist = distance_matrix[route[i - 1]][route[j]] + distance_matrix[route[i]][route[j + 1]]

                    if new_dist < old_dist:
                        route[i : j + 1] = reversed(route[i : j + 1])
                        improved = True
                        break

                if improved:
                    break

        return route

    def _calculate_route_details(self, optimized_route, locations, distance_matrix, vehicle_capacity):
        """Calculate detailed route information"""
        total_distance = 0.0
        route_sequence = []
        total_quantity = 0.0

        for i in range(len(optimized_route) - 1):
            from_idx = optimized_route[i]
            to_idx = optimized_route[i + 1]

            distance = distance_matrix[from_idx][to_idx]
            total_distance += distance

            location = locations[to_idx]
            route_sequence.append(
                {
                    'sequence': i + 1,
                    'location_id': location['id'],
                    'location_name': location['location_name'],
                    'type': location['type'],
                    'distance_from_previous_km': round(distance, 2),
                    'cumulative_distance_km': round(total_distance, 2),
                    'estimated_time_minutes': round(distance * 2, 0),  # assume 30 km/h
                }
            )

            total_quantity += self._to_number(location.get('quantity', 0))

        # Calculate efficiency metrics
        total_time = total_distance * 2  # minutes (assume 30 km/h)
        raw_efficiency = (100 - (total_distance / (max(1, len(locations)) * 10) * 100)) * (
            total_quantity / max(1.0, vehicle_capacity)
        )
        co2_saved = total_distance * 0.21 * 0.75  # 0.21 kg per km, 25% reduction vs individual trips

        return {
            'route': route_sequence,
            'total_distance': total_distance,
            'total_time': total_time,
            'stops': max(0, len(locations) - 1),
            'efficiency_score': min(100.0, max(0.0, raw_efficiency)),
            'capacity_used': total_quantity,
            'capacity_used_percent': (total_quantity / max(1.0, vehicle_capacity)) * 100,
            'co2_saved': co2_saved,
        }

    def _cluster_locations(self, locations, num_clusters):
        """Cluster locations using a simple balanced coordinate sort."""
        if not locations:
            return [[] for _ in range(num_clusters)]

        clusters = [[] for _ in range(num_clusters)]

        def _score(loc):
            lat, lon = self._extract_coordinates(loc)
            return lat + lon

        sorted_locations = sorted(locations, key=_score)

        for idx, location in enumerate(sorted_locations):
            cluster_idx = idx % num_clusters
            clusters[cluster_idx].append(location)

        return clusters

    def _limit_results(self, cursor_or_list, limit):
        """Limit Mongo cursor or plain list to requested size."""
        if hasattr(cursor_or_list, 'limit'):
            return list(cursor_or_list.limit(limit))
        return list(cursor_or_list)[:limit]

    def _find_documents(self, collection, query):
        """Find documents for Mongo or mock collection."""
        result = collection.find(query)
        return list(result)

    def _count_documents(self, collection, query):
        """Count documents for Mongo or mock collection."""
        if hasattr(collection, 'count_documents'):
            return collection.count_documents(query)
        return len(self._find_documents(collection, query))

    @staticmethod
    def _to_number(value, default=0.0):
        try:
            return float(value)
        except Exception:
            return float(default)
