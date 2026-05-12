"""Driver ranking and matching service for ride assignment."""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx

from models.ride import Ride
from repositories.n8n_workflow_log_repository import N8nWorkflowLogRepository


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RankedDriver:
    """Driver with calculated ranking score."""
    driver_id: UUID
    full_name: str
    email: str
    rating: Decimal
    total_rides: int
    distance_km: float
    score: float

    def __lt__(self, other: RankedDriver) -> bool:
        """Enable sorting by score (highest first)."""
        return self.score > other.score


class DriverRankingService:
    """Service for ranking drivers based on multiple criteria.
    
    Scoring factors (pluggable for n8n integration later):
    - Distance (40%): Closer drivers preferred
    - Rating (30%): Higher rated drivers preferred
    - Experience (20%): More completed rides preferred
    - Availability history (10%): Recently accepted drivers preferred
    
    This service is designed to be extended or swapped with external AI ranking
    (e.g., n8n webhook) without changing the matching workflow.
    """

    # Earth radius in kilometers (used for haversine distance calculation)
    EARTH_RADIUS_KM = 6371.0
    
    # Default search radius in kilometers
    DEFAULT_SEARCH_RADIUS_KM = 5.0
    
    # Scoring weights (sum = 1.0)
    WEIGHT_DISTANCE = 0.40
    WEIGHT_RATING = 0.30
    WEIGHT_EXPERIENCE = 0.20
    WEIGHT_AVAILABILITY = 0.10

    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two points using haversine formula.
        
        Args:
            lat1, lon1: Pickup location (latitude, longitude)
            lat2, lon2: Driver location (latitude, longitude)
            
        Returns:
            Distance in kilometers
        """
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return DriverRankingService.EARTH_RADIUS_KM * c

    @classmethod
    def score_driver(
        cls,
        driver_id: UUID,
        full_name: str,
        email: str,
        rating: Decimal,
        total_rides: int,
        distance_km: float,
        max_search_radius_km: float = DEFAULT_SEARCH_RADIUS_KM,
        acceptance_rate: float = 1.0,
    ) -> float:
        """Calculate ranking score for a driver.
        
        Higher score = better match. Score is 0-100.
        
        Args:
            driver_id: Driver UUID
            full_name: Driver name
            email: Driver email
            rating: Driver rating (0-5)
            total_rides: Total completed rides
            distance_km: Distance from pickup location
            max_search_radius_km: Max search radius for normalization
            acceptance_rate: Ratio of accepted to offered rides (0-1)
            
        Returns:
            Score from 0-100
        """
        # Distance score: 0-100, closer = higher
        # Normalize: at max_search_radius_km = 0, at 0km = 100
        distance_score = max(0, 100 - (distance_km / max_search_radius_km * 100))
        
        # Rating score: 0-100, normalized from 0-5
        rating_float = float(rating)
        rating_score = (rating_float / 5.0) * 100
        
        # Experience score: 0-100, normalized logarithmically
        # 1 ride = 50 points, 10 rides = 75 points, 100 rides = 100 points
        if total_rides == 0:
            experience_score = 0
        else:
            # Logarithmic scale: log2(rides + 1) / 7 * 100 (caps at ~100 for 128+ rides)
            experience_score = min(100, (math.log2(total_rides + 1) / 7.0) * 100)
        
        # Availability score: 0-100, based on acceptance rate
        availability_score = acceptance_rate * 100
        
        # Composite score with weights
        score = (
            distance_score * cls.WEIGHT_DISTANCE
            + rating_score * cls.WEIGHT_RATING
            + experience_score * cls.WEIGHT_EXPERIENCE
            + availability_score * cls.WEIGHT_AVAILABILITY
        )
        
        return score

    @classmethod
    def rank_drivers(
        cls,
        drivers: list[dict],
        pickup_latitude: float,
        pickup_longitude: float,
        driver_locations: dict[UUID, tuple[float, float]] | None = None,
        max_search_radius_km: float = DEFAULT_SEARCH_RADIUS_KM,
    ) -> list[RankedDriver]:
        """Rank a list of drivers by score.
        
        Args:
            drivers: List of driver dicts with keys: id, full_name, email, rating, total_rides
            pickup_latitude: Pickup location latitude
            pickup_longitude: Pickup location longitude
            driver_locations: Dict mapping driver_id -> (latitude, longitude).
                            If not provided, drivers are ranked by rating/experience only.
            max_search_radius_km: Max distance to consider driver (km)
            
        Returns:
            List of RankedDriver objects, sorted by score (highest first).
            Drivers outside max_search_radius_km are filtered out.
        """
        ranked = []
        
        for driver in drivers:
            driver_id = driver["id"]
            
            # Get driver location (default to dummy coordinates if not provided)
            if driver_locations and driver_id in driver_locations:
                driver_lat, driver_lon = driver_locations[driver_id]
            else:
                # Without real location data, use default (0, 0) for non-distance-based ranking
                # This allows the service to work even without location tracking
                driver_lat, driver_lon = 0.0, 0.0
            
            # Calculate distance using haversine
            distance = cls.haversine_distance(
                pickup_latitude,
                pickup_longitude,
                driver_lat,
                driver_lon,
            )
            
            # Skip drivers outside search radius
            if distance > max_search_radius_km and driver_locations:
                continue
            
            # Calculate score
            score = cls.score_driver(
                driver_id=driver_id,
                full_name=driver["full_name"],
                email=driver["email"],
                rating=Decimal(str(driver["rating"])),
                total_rides=driver["total_rides"],
                distance_km=distance,
                max_search_radius_km=max_search_radius_km,
                acceptance_rate=1.0,
            )
            
            ranked.append(
                RankedDriver(
                    driver_id=driver_id,
                    full_name=driver["full_name"],
                    email=driver["email"],
                    rating=Decimal(str(driver["rating"])),
                    total_rides=driver["total_rides"],
                    distance_km=distance,
                    score=score,
                )
            )
        
        # Sort by score descending
        ranked.sort()
        return ranked


class RankingProvider:
    """Abstract base for ranking providers (supports n8n webhook injection).
    
    This allows swapping the local ranking algorithm with an external service
    (e.g., n8n AI workflow) without changing the matching service interface.
    """

    async def rank_drivers(
        self,
        ride: Ride,
        available_drivers: list[dict],
    ) -> list[RankedDriver]:
        """Rank available drivers for a ride.
        
        Should be implemented by subclasses (local or external ranking).
        
        Args:
            ride: The Ride object with pickup coordinates
            available_drivers: List of available driver dicts
            
        Returns:
            Ranked list of RankedDriver objects
        """
        raise NotImplementedError


class LocalRankingProvider(RankingProvider):
    """Local ranking implementation using DriverRankingService."""

    def __init__(self, max_search_radius_km: float = DriverRankingService.DEFAULT_SEARCH_RADIUS_KM):
        self.max_search_radius_km = max_search_radius_km

    async def rank_drivers(
        self,
        ride: Ride,
        available_drivers: list[dict],
    ) -> list[RankedDriver]:
        """Rank drivers using local algorithm."""
        if ride.pickup_latitude is None or ride.pickup_longitude is None:
            raise ValueError("Ride must have pickup_latitude and pickup_longitude for ranking")
        
        return DriverRankingService.rank_drivers(
            drivers=available_drivers,
            pickup_latitude=float(ride.pickup_latitude),
            pickup_longitude=float(ride.pickup_longitude),
            driver_locations=None,  # Location tracking not yet implemented
            max_search_radius_km=self.max_search_radius_km,
        )


class N8nRankingProvider(RankingProvider):
    """External ranking provider backed by an n8n webhook.

    Expected n8n response payload supports either of these formats:

    1) {"ranked_drivers": [{"driver_id": "...", "score": 92.1, "distance_km": 1.2}, ...]}
    2) {"ordered_driver_ids": ["uuid-1", "uuid-2", ...]}

    If the webhook call fails or returns an invalid payload, this provider can
    automatically fallback to a local ranking provider.
    """

    def __init__(
        self,
        webhook_url: str,
        timeout_seconds: float = 2.5,
        fallback_provider: RankingProvider | None = None,
        auth_header: str | None = None,
        workflow_log_repository: N8nWorkflowLogRepository | None = None,
    ) -> None:
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds
        self.fallback_provider = fallback_provider
        self.auth_header = auth_header
        self.workflow_log_repository = workflow_log_repository

    async def _record_workflow_log(
        self,
        *,
        status: str,
        ride: Ride,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        if self.workflow_log_repository is None:
            return

        try:
            await self.workflow_log_repository.create_log(
                workflow_name="driver_ranking",
                status=status,
                source="ranking_provider",
                related_entity_type="ride",
                related_entity_id=ride.id,
                request_payload=request_payload,
                response_payload=response_payload,
                error_message=error_message,
            )
        except Exception:
            logger.exception("Failed to record n8n workflow log")

    async def rank_drivers(
        self,
        ride: Ride,
        available_drivers: list[dict],
    ) -> list[RankedDriver]:
        if ride.pickup_latitude is None or ride.pickup_longitude is None:
            raise ValueError("Ride must have pickup_latitude and pickup_longitude for ranking")

        if not available_drivers:
            return []

        payload = {
            "ride": {
                "id": str(ride.id),
                "pickup_latitude": float(ride.pickup_latitude),
                "pickup_longitude": float(ride.pickup_longitude),
                "origin": ride.origin,
                "destination": ride.destination,
                "ride_type": ride.ride_type.value,
            },
            "available_drivers": [
                {
                    "id": str(driver["id"]),
                    "full_name": driver["full_name"],
                    "email": driver["email"],
                    "rating": float(driver["rating"]),
                    "total_rides": int(driver["total_rides"]),
                }
                for driver in available_drivers
            ],
        }

        await self._record_workflow_log(
            status="triggered",
            ride=ride,
            request_payload=payload,
        )

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.auth_header:
            headers["Authorization"] = self.auth_header

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(self.webhook_url, json=payload, headers=headers)
                response.raise_for_status()
                body = response.json()
            ranked = self._parse_n8n_response(body, ride, available_drivers)
            if not ranked:
                raise ValueError("n8n returned no ranked drivers")
            await self._record_workflow_log(
                status="success",
                ride=ride,
                request_payload=payload,
                response_payload={"response": body, "ranked_driver_count": len(ranked)},
            )
            return ranked
        except Exception as exc:
            await self._record_workflow_log(
                status="failed" if self.fallback_provider is None else "fallback",
                ride=ride,
                request_payload=payload,
                error_message=str(exc),
            )
            if self.fallback_provider is None:
                raise
            logger.warning(
                "n8n ranking failed; falling back to local ranking",
                extra={"reason": str(exc), "ride_id": str(ride.id)},
            )
            return await self.fallback_provider.rank_drivers(ride, available_drivers)

    @staticmethod
    def _parse_n8n_response(
        body: Any,
        ride: Ride,
        available_drivers: list[dict],
    ) -> list[RankedDriver]:
        """Normalize n8n webhook response into RankedDriver objects."""
        if not isinstance(body, dict):
            raise ValueError("Invalid n8n response: expected JSON object")

        by_id: dict[str, dict] = {str(driver["id"]): driver for driver in available_drivers}
        ranked: list[RankedDriver] = []

        ranked_payload = body.get("ranked_drivers")
        if isinstance(ranked_payload, list):
            for index, item in enumerate(ranked_payload):
                if not isinstance(item, dict):
                    continue
                raw_driver_id = item.get("driver_id") or item.get("id")
                if raw_driver_id is None:
                    continue
                driver_id = str(raw_driver_id)
                driver = by_id.get(driver_id)
                if driver is None:
                    continue

                distance_km = item.get("distance_km")
                if distance_km is None:
                    distance_km = DriverRankingService.haversine_distance(
                        float(ride.pickup_latitude),
                        float(ride.pickup_longitude),
                        0.0,
                        0.0,
                    )

                score = item.get("score")
                if score is None:
                    score = float(max(0, len(ranked_payload) - index))

                ranked.append(
                    RankedDriver(
                        driver_id=UUID(driver_id),
                        full_name=driver["full_name"],
                        email=driver["email"],
                        rating=Decimal(str(driver["rating"])),
                        total_rides=int(driver["total_rides"]),
                        distance_km=float(distance_km),
                        score=float(score),
                    )
                )
            ranked.sort()
            return ranked

        ordered_ids = body.get("ordered_driver_ids")
        if isinstance(ordered_ids, list):
            for index, raw_driver_id in enumerate(ordered_ids):
                driver_id = str(raw_driver_id)
                driver = by_id.get(driver_id)
                if driver is None:
                    continue
                ranked.append(
                    RankedDriver(
                        driver_id=UUID(driver_id),
                        full_name=driver["full_name"],
                        email=driver["email"],
                        rating=Decimal(str(driver["rating"])),
                        total_rides=int(driver["total_rides"]),
                        distance_km=0.0,
                        score=float(max(0, len(ordered_ids) - index)),
                    )
                )
            ranked.sort()
            return ranked

        raise ValueError("Invalid n8n response: expected ranked_drivers or ordered_driver_ids")
