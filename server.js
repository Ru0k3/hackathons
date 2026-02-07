import express from "express";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();
const app = express();
app.use(express.json());

const PORT = process.env.PORT || 4000;
const BD_KEY = process.env.BETTERDOCTOR_KEY;

/*
---------------------------------------------------
 HEALTH CHECK
---------------------------------------------------
*/
app.get("/api/health", (req, res) => {
  res.json({
    status: "OK",
    message: "Medical Reference API running",
  });
});

/*
---------------------------------------------------
 DOCTOR SEARCH (REFERENCE ONLY)
 Source: BetterDoctor API / ABDM (India compatible)
---------------------------------------------------
*/
app.get("/api/doctors", async (req, res) => {
  const { name, specialty, location } = req.query;

  if (!BD_KEY || BD_KEY === "YOUR_API_KEY_HERE") {
    // Return mock data if key is missing/default
    return res.json({
      source: "Mock Data (API Key Missing)",
      results: [
        { profile: { first_name: "Sarah", last_name: "Smith", title: "MD", bio: "Emergency Medicine Specialist" } },
        { profile: { first_name: "James", last_name: "Chen", title: "MD", bio: "Internal Medicine" } }
      ]
    });
  }

  try {
    const url = `https://api.betterdoctor.com/2016-03-01/doctors?name=${name || ""}&specialty_uid=${specialty || ""}&location=${location || ""}&skip=0&limit=5&user_key=${BD_KEY}`;
    const response = await axios.get(url);

    res.json({
      source: "BetterDoctor",
      results: response.data.data,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/*
---------------------------------------------------
 MEDICINE / DRUG INFO (SAFETY, WARNINGS, LABELS)
 Source: openFDA (PUBLIC, NO KEY REQUIRED)
---------------------------------------------------
*/
app.get("/api/drugs", async (req, res) => {
  const { name } = req.query;

  if (!name) {
    return res.status(400).json({
      error: "Drug name required",
    });
  }

  try {
    const url = `https://api.fda.gov/drug/label.json?search=openfda.generic_name:"${name}"&limit=1`;
    const response = await axios.get(url);

    const result = response.data.results[0];
    res.json({
      source: "openFDA",
      drug: name,
      warnings: result.warnings ? result.warnings[0] : "No specific warning found.",
      purpose: result.purpose ? result.purpose[0] : "No purpose listed.",
      dosage: result.dosage_and_administration ? result.dosage_and_administration[0] : "Consult physician for dosage.",
      active_ingredient: result.active_ingredient ? result.active_ingredient[0] : name
    });
  } catch (err) {
    // Fallback if not found or error
    res.json({
      source: "Local Fallback",
      drug: name,
      warnings: "Consult a doctor before use.",
      purpose: "General use."
    });
  }
});

/*
---------------------------------------------------
 TRIAGE-SAFE DISCLAIMER ENDPOINT
---------------------------------------------------
*/
app.get("/api/disclaimer", (req, res) => {
  res.json({
    warning:
      "This system does NOT prescribe medicines or replace professional medical advice.",
    purpose:
      "Reference information only. Always consult a licensed doctor.",
  });
});

/*
---------------------------------------------------
 START SERVER
---------------------------------------------------
*/
app.listen(PORT, () => {
  console.log(`🚑 Medical Reference API running on port ${PORT}`);
});
