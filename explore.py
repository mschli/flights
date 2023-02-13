
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from skyscanner.skyscanner import Flights
import pandas as pd

flights_service = Flights('prtl6749387986743898559646983194')

@dataclass
class Flight:
    departure: datetime
    arrival: datetime
    stops: int
    price: float
    link: str

def get_cheapest_flight(origin: str, destination: str, date: datetime, not_before: time, not_after: time) -> list[Flight]:
    data = flights_service.get_result(
        country='DE',
        currency='EUR',
        locale='de-DE',
        originplace=origin,
        destinationplace=destination,
        outbounddate=date.strftime("%Y-%m-%d"),
        adults=1).parsed

    flights = []

    for leg in data["Legs"]:
        id = leg["Id"]
        itinerary = next((x for x in data["Itineraries"] if x["OutboundLegId"] == id), None)
        if itinerary == None:
            continue
        flights.append(
            Flight(
                departure=datetime.strptime(leg["Departure"], '%Y-%m-%dT%H:%M:%S'),
                arrival=datetime.strptime(leg["Arrival"], '%Y-%m-%dT%H:%M:%S'),
                stops=len(leg["Stops"]),
                price=itinerary["PricingOptions"][0]["Price"],
                link = itinerary["PricingOptions"][0]["DeeplinkUrl"]
             )
        )

    def is_in_timeslot(flight: Flight, start: time, end: time):
        t = flight.departure.time()
        return (t > start and t < end)

    filtered_flights = [flight for flight in flights if (is_in_timeslot(flight, not_before, not_after) and flight.stops == 0)]
    return min(filtered_flights, key=lambda x: x.price)

df = pd.DataFrame(columns=['departure', 'arrival', 'price', 'link'])

start_date = datetime(2023, 4, 4)
end_date = datetime(2023, 11, 28)

delta = timedelta(days=7)
while start_date <= end_date:
    outbound_flight = get_cheapest_flight('MUC-sky', 'CGN-sky', start_date, time(6, 0), time(8, 0))
    return_flight = get_cheapest_flight( 'CGN-sky', 'MUC-sky', start_date + timedelta(days=2), time(20, 0), time(23, 59))
    
    df.loc[start_date] = [outbound_flight.departure, outbound_flight.arrival, outbound_flight.price, outbound_flight.link]
    df.loc[start_date + timedelta(days=2)] = [return_flight.departure, return_flight.arrival, return_flight.price, return_flight.link]
    start_date += delta
    print(start_date)

df.to_csv("output.csv", sep=',', index=False)