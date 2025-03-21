"""Creates a turnstile data producer"""
import logging
from pathlib import Path

from confluent_kafka import avro

from models.producer import Producer
from models.turnstile_hardware import TurnstileHardware


logger = logging.getLogger(__name__)


class Turnstile(Producer):
    
    # events are paired with the Avro key and value schemas
    key_schema = avro.load(f"{Path(__file__).parents[0]}/schemas/turnstile_key.json")
    value_schema = avro.load(
       f"{Path(__file__).parents[0]}/schemas/turnstile_value.json"
    )

    def __init__(self, station):
        """Create the Turnstile"""
        station_name = (
            station.name.lower()
            .replace("/", "_and_")
            .replace(" ", "_")
            .replace("-", "_")
            .replace("'", "")
        )

        #
        #
        # TODO: Complete the below by deciding on a topic name, number of partitions, and number of
        # replicas
        #
        #
        super().__init__(
#             topic_name=f"turnstile.station.{station_name}", # TODO: Come up with a better topic name
            topic_name='turnstile_station',
            key_schema=Turnstile.key_schema,
            value_schema=Turnstile.value_schema,
            num_partitions=3,
            num_replicas=1,
        )
        
        self.station = station
        self.turnstile_hardware = TurnstileHardware(station)

    def run(self, timestamp, time_step):
        """Simulates riders entering through the turnstile."""
        num_entries = self.turnstile_hardware.get_entries(timestamp, time_step)
#         logger.info(f"Processing {num_entries} entries for turnstile at {timestamp}.")
        
        #
        #
        # TODO: Complete this function by emitting a message to the turnstile topic for the number
        # of entries that were calculated
        #
        #
        try:
            for _ in range(num_entries):
                self.producer.produce(
                        topic=self.topic_name,
                        key_schema=self.key_schema,
                        key={"timestamp": self.time_millis()},
                        value_schema=self.value_schema,
                        value={
                                "station_id"  : self.station.station_id,
                                "station_name": self.station.name,
                                "line"        : self.station.color.name
                        },
                )
        except:
            logger.info("turnstile kafka integration incomplete - skipping")