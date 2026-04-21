from flask import Flask, request, render_template_string
import pandas as pd
import json

# ======================================================
# REAL HISTORICAL GOLD PRICES (₹ per 10g approx)
# ======================================================

historical_prices = {
2000:4400,2001:4300,2002:4990,2003:5600,2004:5850,
2005:7000,2006:8400,2007:10800,2008:12500,2009:14500,
2010:18500,2011:26400,2012:31050,2013:29600,2014:28000,
2015:26300,2016:28600,2017:29650,2018:31400,2019:35200,
2020:48600,2021:48720,2022:52800,2023:60300,
2024:65000,2025:72000
}

# ======================================================
# FUTURE PREDICTION (SMOOTH COMPOUND GROWTH)
# ======================================================

future_prices = {
2026:160000,
2027:180000,
2028:200000
}

last_price = 200000

for year in range(2029, 2081):
    last_price = last_price * 1.05
    future_prices[year] = round(last_price)

# Merge
all_prices = {**historical_prices, **future_prices}

# ======================================================
# DATAFRAME
# ======================================================

df = pd.DataFrame({
    "Year": list(all_prices.keys()),
    "Price": list(all_prices.values())
})

df = df.sort_values("Year")

# Moving Average
df["MA5"] = df["Price"].rolling(5).mean().bfill()

# ======================================================
# FLASK APP
# ======================================================

app = Flask(__name__)

HTML = """

<!DOCTYPE html>
<html>
<head>
<title>Gold Analytics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
body{
    font-family: Segoe UI;
    background: #ffffff;
    color: #0f172a;
    padding: 30px;
}

h1{
    color: #b45309;
    text-align: center;
}

.card{
    background: #f8fafc;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

button{
    padding: 10px 15px;
    background: #facc15;
    border: none;
    border-radius: 6px;
    font-weight: bold;
    cursor: pointer;
}

button:hover{
    background: #eab308;
}

input{
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
}

h2{
    color: #1e293b;
}

h3{
    color: #16a34a;
}
</style>

</head>

<body>

<h1>Gold Price Analytics Dashboard (2000 - 2080)</h1>

<div class="card">
<h2>Gold Price Trend</h2>
<canvas id="trendChart"></canvas>
</div>

<div class="card">
<h2>Moving Average Trend</h2>
<canvas id="maChart"></canvas>
</div>

<div class="card">
<h2>Prediction</h2>
<canvas id="predChart"></canvas>
</div>

<div class="card">
<h2>Predict Gold Price</h2>

<form method="post">
<input type="number" name="year" placeholder="Enter Year (2035)" required>
<button type="submit">Predict</button>
</form>

<h3>{{prediction}}</h3>

</div>

<script>

const years = {{years|safe}}
const prices = {{prices|safe}}
const ma = {{ma|safe}}

const pred_year = {{pred_year|safe}}
const pred_price = {{pred_price|safe}}

// Trend Chart
new Chart(document.getElementById("trendChart"),{
 type:'line',
 data:{
  labels:years,
  datasets:[
   {
    label:'Gold Price ₹',
    data:prices,
    borderColor:'#f59e0b',
    backgroundColor:'rgba(245,158,11,0.2)',
    tension:0.3
   }
  ]
 }
})

// Moving Average Chart
new Chart(document.getElementById("maChart"),{
 type:'line',
 data:{
  labels:years,
  datasets:[
   {
    label:'Moving Average',
    data:ma,
    borderColor:'#16a34a',
    backgroundColor:'rgba(22,163,74,0.2)',
    tension:0.3
   }
  ]
 }
})

// Prediction Chart
new Chart(document.getElementById("predChart"),{
 type:'scatter',
 data:{
  datasets:[
   {
    label:'Prediction',
    data: pred_year ? [{x:pred_year,y:pred_price}] : [],
    backgroundColor:'#dc2626',
    pointRadius:10
   }
  ]
 },
 options:{
  plugins:{
   tooltip:{
    callbacks:{
     label:function(context){
      return "Year: " + context.raw.x + " | Price: ₹" + context.raw.y;
     }
    }
   }
  },
  scales:{
   x:{
    type:'linear',
    title:{display:true,text:'Year',color:'#000'},
    ticks:{color:'#000'}
   },
   y:{
    title:{display:true,text:'Gold Price ₹',color:'#000'},
    ticks:{color:'#000'}
   }
  }
 }
})

</script>

</body>
</html>

"""

@app.route("/", methods=["GET", "POST"])
def home():

    prediction = ""
    pred_year = None
    pred_price = None

    if request.method == "POST":
        year = int(request.form["year"])

        if year in all_prices:
            pred_price = all_prices[year]
        else:
            pred_price = df["Price"].iloc[-1] * 1.05

        prediction = f"Predicted Gold Price for {year}: ₹{round(pred_price)}"

        pred_year = year
        pred_price = round(pred_price)

    return render_template_string(
        HTML,
        prediction=prediction,
        years=json.dumps(df["Year"].tolist()),
        prices=json.dumps(df["Price"].tolist()),
        ma=json.dumps(df["MA5"].tolist()),
        pred_year=json.dumps(pred_year),
        pred_price=json.dumps(pred_price)
    )

if __name__ == "__main__":
    app.run(debug=True)
