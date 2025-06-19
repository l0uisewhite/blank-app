import streamlit as st
import pandas as pd
import gspread
# from oauth2client.service_account import ServiceAccountCredentials
import json
from google.oauth2 import service_account
import datetime

st.set_page_config(layout="centered")
st.sidebar.title("Navigation")
page = st.sidebar.radio(
            "Go to", 
            ["Home", "Pub Tracker", "Leaderboard", "Scorecard"]
)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = dict(st.secrets["gcp_service_account"])
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
client = gspread.authorize(creds)

if page == "Home":
    st.title("NetChix Pub Golf")
    st.write(
    "Let's Start Drinking"
)
    st.subheader("🍻 The Official Crawl Route")
    pubs = """ 
        Liv's 🍺
        Devonshire 🍺
        Avalon 🍺
        Park 🍺
        The Alexandra 🍺
        Clapham North 🍺
        The Falcon 🍺
        Hope and Anchor 🍺
        Alice's 🍺
    """
    st.markdown(pubs)


elif page == "Pub Tracker":
    st.title("🏁 Enter Your Scores")
    
    # Define par values for each pub (adjust these as needed)
    PAR_VALUES = {
        "Liv's": 5,
        "Devonshire": 2,
        "Avalon": 1,
        "Park": 5,
        "The Alexandra": 3,
        "Clapham North": 2,
        "The Falcon": 4,
        "Hope and Anchor": 5,
        "Alice's": 4
    }
    
    
    with st.form("score_form"):
        name = st.text_input("Your Name")
        pub = st.selectbox("Which pub did you just visit?", [
            "Liv's", "Devonshire", "Avalon", "Park", 
            "The Alexandra", "Clapham North", 
            "The Falcon", "Hope and Anchor", "Alice's"
        ])
        score = st.number_input("Score (1 = hole-in-one 🍺)", min_value=1, max_value=10)
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Calculate difference from par
            par = PAR_VALUES[pub]
            difference = score - par
            
            # Prepare data to write to Google Sheets
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = [timestamp, name, pub, par, score, difference]
            sheet = client.open("netchix_pub_leaderboard").get_worksheet(1)
                
            # Append the new row
            sheet.append_row(data)
            
            # Show success message with difference
            if difference < 0:
                message = f"⛳ {name} scored {score} at {pub} (UNDER par by {abs(difference)})"
            elif difference == 0:
                message = f"⛳ {name} scored {score} at {pub} (EXACTLY par!)"
            else:
                message = f"⛳ {name} scored {score} at {pub} (OVER par by {difference})"
            
            st.success(message)
            st.balloons()
            
            st.success(f"Score recorded for {name} at {pub}!")
            

    

# elif page == "Pub Location":
    
   

elif page == "Leaderboard":
    st.title("📊 Live Leaderboard")
    sheet = client.open("netchix_pub_leaderboard").get_worksheet(1) 
    
    # Get all records
    records = sheet.get_all_records()  
    
    # Calculate total scores per person
    scores = {}
    for row in records:
        name = row['Name']
        score = int(row['Difference'])
        scores[name] = scores.get(name, 0) + score
    
    # Sort by score (ascending - lower score = better)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    
    # Display leaderboard
    st.subheader("Current Rankings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Rank**")
        for i in range(len(sorted_scores)):
            st.write(f"{i+1}.")
    
    with col2:
        st.markdown("**Player | Total Score**")
        for name, total in sorted_scores:
            st.write(f"{name} | {total}")
            
    if len(sorted_scores) > 0:
        winner, winning_score = sorted_scores[0]
        st.balloons()
        st.success(f"🏆 Current leader: {winner} with {winning_score} points!")



elif page == "Scorecard":
    st.title("Scorecard")
    sheet = client.open("netchix_pub_leaderboard").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    st.dataframe(df)