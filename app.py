import streamlit as st
# python3 -m streamlit run app.py
from amadeus import Client, ResponseError
import datetime
import ssl

# Logo URL
logo_url = "https://upload.wikimedia.org/wikipedia/commons/5/57/Airplane_silhouette_S.png"

st.sidebar.image(
    logo_url,
    width=200, 
    caption="SkyLine Saver", 
)

# Disable SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Initialize Amadeus Client
amadeus = Client(
    client_id="",  # API Key
    client_secret=""  # API Secret
)

# Sidebar for navigation
st.sidebar.title("Navigation")
main_pages = ["Home", "Flight Price Optimizer", "About Us", "Support"]
selected_page = st.sidebar.radio("Select a page:", main_pages)

# Handle sidebar navigation
st.session_state.page = selected_page

# App logic
if st.session_state.page == "Home":
    st.title("Welcome to SkyLine Saver")
    st.write("Flight Price Optimizer")

elif st.session_state.page == "Flight Price Optimizer":
    st.title("Find the Best Prices for Flights")
    st.write("Use the filters below to search for the best flight prices.")
    st.write("The best deals are displayed first.")

    # Flight filter inputs
    departure = st.text_input("Departure Airport IATA Code (e.g., JFK, YYZ, FCO)", placeholder="e.g., JFK, YYZ, FCO")
    destination = st.text_input("Destination Airport IATA Code (e.g., LAX, YUL, CDG)", placeholder="e.g., LAX, YUL, CDG")
    departure_date = st.date_input("Departure Date", min_value=datetime.date.today())
    return_date = st.date_input("Return Date (optional)", min_value=departure_date)
    price_range = st.slider("Maximum Price ($)", min_value=50, max_value=5000, value=1000, step=50)
    passengers = st.number_input("Number of Passengers", min_value=1, max_value=10, value=1)

    # Search button
    if st.button("Search Flights"):
        # Validate inputs
        if not departure or len(departure) != 3 or not departure.isalpha():
            st.warning("Please enter a valid IATA code for departure.")
        elif not destination or len(destination) != 3 or not destination.isalpha():
            st.warning("Please enter a valid IATA code for destination.")
        else:
            try:
                # Call Amadeus API
                response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=departure.upper(),
                    destinationLocationCode=destination.upper(),
                    departureDate=departure_date.strftime("%Y-%m-%d"),
                    returnDate=return_date.strftime("%Y-%m-%d") if return_date else None,
                    adults=passengers,
                    maxPrice=price_range
                )

                flights = response.data  # List of flight offers
                if flights:
                    st.success(f"Found {len(flights)} flights!")
                    for flight in flights:
                        itinerary = flight["itineraries"][0]
                        price = flight["price"]["total"]
                        duration = itinerary["duration"]

                        st.write(f"**Price:** ${price}")
                        st.write(f"**Duration:** {duration}")
                        for segment in itinerary["segments"]:
                            departure_info = segment["departure"]
                            arrival_info = segment["arrival"]
                            airline = segment["carrierCode"]  # Extract airline carrier code
                            st.write(f"- **Airline:** {airline}")
                            st.write(f"- **From:** {departure_info['iataCode']} at {departure_info['at']}")
                            st.write(f"- **To:** {arrival_info['iataCode']} at {arrival_info['at']}")
                else:
                    st.warning("No flights found for the selected criteria.")

            except ResponseError as error:
                try:
                    # Log the entire response for debugging
                    st.write("Full error response:", error.response)
                    # Check if response data is None
                    if error.response.data:
                        # Access the error response data directly
                        error_detail = error.response.data  # Get the response data attribute directly
                        if "errors" in error_detail and len(error_detail["errors"]) > 0:
                            st.error(f"API Error: {error_detail['errors'][0].get('detail', 'Unknown error detail')}")
                        else:
                            st.error("An unexpected error occurred while fetching flight data.")
                    else:
                        st.error("No error details available from the API response.")
                except Exception as e:
                    # Fallback error handling
                    st.error(f"An error occurred while processing the error response: {str(e)}")

elif st.session_state.page == "About Us":
    st.title("About Us")
    st.write("Welcome to SkyLine Saver! Our goal is to help you find the best flight prices with ease.")
    st.write(
        """
        SkyLine Saver leverages advanced technology to provide real-time flight offers, helping you save money 
        and time. Whether you're planning a vacation or a business trip you will find the most optmized flight for your needs here.
        """
    )

elif st.session_state.page == "Support":
    st.title("Support")

    # Support Sub Pages
    support_pages = ["Contact Support", "FAQ"]
    selected_support_page = st.sidebar.radio("Support Options:", support_pages)

    if selected_support_page == "Contact Support":
        st.header("Contact Support")
        st.write("If you encounter any issues contact us by email or call the number below")
        st.write("Email: Skylinesaver@gmail.ca")
        st.write("Phone Number: 6476799717")

    elif selected_support_page == "FAQ":
        st.header("Frequently Asked Questions (FAQ)")
        st.markdown('**What do I need to input for departure and destination locations?**')  
        st.write(" You need to input the IATA airport code for the airports you want to fly in or out of")
        st.markdown('**The IATA Code is not working?**') 
        st.write(" Make sure the three letter code is correct for your destination and is in all capital letters")
        st.markdown('**Is the app free?**')
        st.write(" Yes the service is 100% free")
        st.markdown('**Is the flight data accurate?**') 
        st.write(" Yes, data is provided in real time from a trusted API")
