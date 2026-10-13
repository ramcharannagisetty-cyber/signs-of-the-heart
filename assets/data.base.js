/* Site settings and non-medical content.
   Medical content (stats, topic guides, tools) lives in data.content.js, which is generated
   from fact-checked research. Edit this file for names, billboards, team and stories. */
window.SITE = {
  org: {
    name: "Signs of the Heart",
  },

  // Every "email us" button goes to all of these addresses at once.
  contact: {
    emails: ["nagisetty.ramcharan@gmail.com", "punjaniarmaan@gmail.com"], // Ramcharan and Armaan
  },

  // Call-to-action cards. Each button opens an email to the founders with this subject line.
  firstOne: {
    team: { title: "Join us", text: "Help us build this: research, design, outreach or putting up billboards.", cta: "Join us", subject: "I want to help build Signs of the Heart", body: "Hi,\n\nI'd like to help build Signs of the Heart. My name is ___ and I can help with ___.\n" },
    advisor: { title: "Be a medical advisor", text: "Are you a cardiologist, nurse or health educator? Help us review our guides.", cta: "Become an advisor", subject: "Medical advisor for Signs of the Heart", body: "Hi,\n\nI'm ___ (role: ___) and I'd be open to reviewing your heart health guides.\n" },
    stories: { title: "Share your story", text: "Has heart disease touched your life or your family's? Share your story here, with your permission.", cta: "Share your story", subject: "My story for Signs of the Heart", body: "Hi,\n\nI'd like to share my story. You may / may not use my name.\n" },
  },

  // Order and look of the condition posters on the homepage wall.
  // span: width on the 6-column wall. tone: poster colour. label/kicker: optional shorter text for the poster.
  wall: [
    { slug: "heart-failure", span: 4, tone: "red", tilt: -0.8, kicker: "Pumping problem" },
    { slug: "fmd-scad", span: 2, tone: "caution", tilt: 1.2, label: "FMD and SCAD" },
    { slug: "hypertension", span: 2, tone: "paper", tilt: 0.6, label: "High blood pressure" },
    { slug: "cholesterol", span: 2, tone: "ecg", tilt: -1 },
    { slug: "bp-and-cholesterol", span: 2, tone: "dark", tilt: 0.9, label: "Blood pressure + cholesterol" },
    { slug: "heart-attack-cpr", span: 3, tone: "dark", tilt: -0.5, label: "Heart attack, cardiac arrest and CPR" },
    { slug: "afib-stroke", span: 3, tone: "paper", tilt: 0.7 },
  ],

  billboards: {
    // 18 finished designs (3 per topic). image = preview, file = full-size 4800 x 1400 JPG, svg = vector for print shops.
    templates: [
      { id: "hf-A", title: "Heart failure", design: "Design A", topic: "heart-failure", image: "assets/billboards/hf-A.jpg", file: "assets/billboards/hf-A-full.jpg", svg: "assets/billboards/hf-A.svg", alt: "Breathless on stairs? Check your heart." },
      { id: "hf-B", title: "Heart failure", design: "Design B", topic: "heart-failure", image: "assets/billboards/hf-B.jpg", file: "assets/billboards/hf-B-full.jpg", svg: "assets/billboards/hf-B.svg", alt: "Swollen ankles? Ask about heart failure." },
      { id: "hf-C", title: "Heart failure", design: "Design C", topic: "heart-failure", image: "assets/billboards/hf-C.jpg", file: "assets/billboards/hf-C-full.jpg", svg: "assets/billboards/hf-C.svg", alt: "Need extra pillows to breathe? Tell your doctor." },
      { id: "fmd-A", title: "FMD and SCAD", design: "Design A", topic: "fmd-scad", image: "assets/billboards/fmd-A.jpg", file: "assets/billboards/fmd-A-full.jpg", svg: "assets/billboards/fmd-A.svg", alt: "Young. Healthy. Chest pain? Call 911." },
      { id: "fmd-B", title: "FMD and SCAD", design: "Design B", topic: "fmd-scad", image: "assets/billboards/fmd-B.jpg", file: "assets/billboards/fmd-B-full.jpg", svg: "assets/billboards/fmd-B.svg", alt: "Heartbeat in your ear? Tell a doctor." },
      { id: "fmd-C", title: "FMD and SCAD", design: "Design C", topic: "fmd-scad", image: "assets/billboards/fmd-C.jpg", file: "assets/billboards/fmd-C-full.jpg", svg: "assets/billboards/fmd-C.svg", alt: "“Too healthy for a heart attack.” Chest pain? Call 911." },
      { id: "bp-A", title: "High blood pressure", design: "Design A", topic: "hypertension", image: "assets/billboards/bp-A.jpg", file: "assets/billboards/bp-A-full.jpg", svg: "assets/billboards/bp-A.svg", alt: "BLOOD PRESSURE LIMIT 120/80. Stay under it. Check yours." },
      { id: "bp-B", title: "High blood pressure", design: "Design B", topic: "hypertension", image: "assets/billboards/bp-B.jpg", file: "assets/billboards/bp-B-full.jpg", svg: "assets/billboards/bp-B.svg", alt: "High blood pressure feels like nothing. Get it checked." },
      { id: "bp-C", title: "High blood pressure", design: "Design C", topic: "hypertension", image: "assets/billboards/bp-C.jpg", file: "assets/billboards/bp-C-full.jpg", svg: "assets/billboards/bp-C.svg", alt: "You check your tire pressure. Check your blood pressure." },
      { id: "chol-A", title: "Cholesterol", design: "Design A", topic: "cholesterol", image: "assets/billboards/chol-A.jpg", file: "assets/billboards/chol-A-full.jpg", svg: "assets/billboards/chol-A.svg", alt: "No symptoms. One blood test. Get your cholesterol checked." },
      { id: "chol-B", title: "Cholesterol", design: "Design B", topic: "cholesterol", image: "assets/billboards/chol-B.jpg", file: "assets/billboards/chol-B-full.jpg", svg: "assets/billboards/chol-B.svg", alt: "Your heart has no warning light. Get a cholesterol test." },
      { id: "chol-C", title: "Cholesterol", design: "Design C", topic: "cholesterol", image: "assets/billboards/chol-C.jpg", file: "assets/billboards/chol-C-full.jpg", svg: "assets/billboards/chol-C.svg", alt: "When was your last cholesterol test? Can't remember? Book one." },
      { id: "cpr-A", title: "Hands-only CPR", design: "Design A", topic: "heart-attack-cpr", image: "assets/billboards/cpr-A.jpg", file: "assets/billboards/cpr-A-full.jpg", svg: "assets/billboards/cpr-A.svg", alt: "Push hard. Push fast. 100–120 a minute. Call 911 first." },
      { id: "cpr-B", title: "Hands-only CPR", design: "Design B", topic: "heart-attack-cpr", image: "assets/billboards/cpr-B.jpg", file: "assets/billboards/cpr-B-full.jpg", svg: "assets/billboards/cpr-B.svg", alt: "Know “Stayin’ Alive”? You know CPR. Call 911. Push to the beat." },
      { id: "cpr-C", title: "Hands-only CPR", design: "Design C", topic: "heart-attack-cpr", image: "assets/billboards/cpr-C.jpg", file: "assets/billboards/cpr-C-full.jpg", svg: "assets/billboards/cpr-C.svg", alt: "Start CPR before help arrives. CPR right away: 2–3× the chance of survival. Call 911. Push hard and fast." },
      { id: "stroke-A", title: "AFib and stroke", design: "Design A", topic: "afib-stroke", image: "assets/billboards/stroke-A.jpg", file: "assets/billboards/stroke-A-full.jpg", svg: "assets/billboards/stroke-A.svg", alt: "Spot a stroke: BE FAST. Balance, Eyes, Face, Arms, Speech, Time: call 911." },
      { id: "stroke-B", title: "AFib and stroke", design: "Design B", topic: "afib-stroke", image: "assets/billboards/stroke-B.jpg", file: "assets/billboards/stroke-B-full.jpg", svg: "assets/billboards/stroke-B.svg", alt: "Face drooping? Ask them to smile. Uneven? Call 911. Every minute counts." },
      { id: "stroke-C", title: "AFib and stroke", design: "Design C", topic: "afib-stroke", image: "assets/billboards/stroke-C.jpg", file: "assets/billboards/stroke-C-full.jpg", svg: "assets/billboards/stroke-C.svg", alt: "Fluttering heartbeat? AFib can lead to stroke. See a doctor." },
    ],
    size: "48 × 14 ft billboard bulletin",
  },

  // PLACEHOLDER stories (not real people). Replace with real ones, shared with permission,
  // then remove "placeholder: true".
  stories: [
    { quote: "A real story from someone living with heart failure will go here, shared with their permission.", name: "Real story coming soon", role: "Heart failure", placeholder: true },
    { quote: "A real story from someone diagnosed with FMD or SCAD will go here, shared with their permission.", name: "Real story coming soon", role: "FMD and SCAD", placeholder: true },
  ],

  // Team. Photos live in assets/team/.
  team: [
    { name: "Ramcharan Nagisetty", role: "Co-founder", photo: "assets/team/ramcharan.jpg" },
    { name: "Armaan Punjani", role: "Co-founder", photo: "assets/team/armaan.jpg" },
  ],

};
