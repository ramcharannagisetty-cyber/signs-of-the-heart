/* Site settings and non-medical content.
   Medical content (stats, topic guides, tools) lives in data.content.js, which is generated
   from fact-checked research. Edit this file for names, billboards, donate, team and stories. */
window.SITE = {
  org: {
    name: "Signs of the Heart",
  },

  // Every "email us" button goes to all of these addresses at once.
  contact: {
    emails: ["nagisetty.ramcharan@gmail.com", "punjaniarmaan@gmail.com"], // Ramcharan and Armaan
  },

  // "Be the first" cards. Each button opens an email to the founders with this subject line.
  firstOne: {
    team: { title: "Be the first to join us", text: "Hello! You can be the first one to help build this: research, design, outreach or putting up billboards.", subject: "I want to help build Signs of the Heart", body: "Hi,\n\nI'd like to help build Signs of the Heart. My name is ___ and I can help with ___.\n" },
    advisor: { title: "Be our first medical advisor", text: "Hello! Are you a cardiologist, nurse or health educator? You can be the first one to review our guides.", subject: "Medical advisor for Signs of the Heart", body: "Hi,\n\nI'm ___ (role: ___) and I'd be open to reviewing your heart health guides.\n" },
    sponsors: { title: "Be our first sponsor", text: "Hello! You can be the first one to sponsor us. Help fund billboards and posters that teach people the signs of heart disease.", subject: "Sponsoring Signs of the Heart", body: "Hi,\n\nI'm ___ from ___. We'd like to talk about sponsoring Signs of the Heart.\n" },
    press: { title: "Be the first to cover us", text: "Hello! You can be the first one to write about our student-led heart health campaign.", subject: "Press inquiry: Signs of the Heart", body: "Hi,\n\nI'm ___ from ___ and I'd like to cover Signs of the Heart.\n" },
    stories: { title: "Be the first to share your story", text: "Hello! Has heart disease touched your life or your family's? You can be the first one to share your story here, with your permission.", subject: "My story for Signs of the Heart", body: "Hi,\n\nI'd like to share my story. You may / may not use my name.\n" },
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
    // PLACEHOLDER template slots. Add an "image" path to show a finished design in the frame,
    // and set "placeholder: false" on that template so its placeholder label goes away.
    templates: [
      { id: "hf-breathless", placeholder: true, title: "Heart failure", topic: "heart-failure" },
      { id: "fmd-whoosh", placeholder: true, title: "FMD and SCAD", topic: "fmd-scad" },
      { id: "bp-silent", placeholder: true, title: "High blood pressure", topic: "hypertension" },
      { id: "chol-numbers", placeholder: true, title: "Cholesterol", topic: "cholesterol" },
      { id: "cpr-push", placeholder: true, title: "Hands-only CPR", topic: "heart-attack-cpr" },
      { id: "stroke-befast", placeholder: true, title: "AFib and stroke", topic: "afib-stroke" },
    ],
    size: "48 × 14 ft billboard bulletin",
    // PLACEHOLDER NUMBERS. Shown with a "Placeholder numbers" label while showPreviewTag is true.
    // For real counts: set all to 0 and set showPreviewTag to false.
    seed: {
      downloads: 1248,
      placed: 37,
      reached: 52400,
      perTemplate: { "hf-breathless": 312, "fmd-whoosh": 148, "bp-silent": 274, "chol-numbers": 166, "cpr-push": 231, "stroke-befast": 117 },
    },
    showPreviewTag: true,
  },

  donate: {
    link: "", // PLACEHOLDER: empty = donations not open yet (button shows "coming soon" + email link)
    placeholder: true, // shows "Placeholder" labels on the goal and amounts
    target: "First billboard: a 4-week highway bulletin",
    goal: 2500, // PLACEHOLDER goal
    raised: 0, // real: donations aren't open yet
    chips: [
      { amount: 10, impact: "$10 prints 5 clinic posters." },
      { amount: 25, impact: "$25 covers a library display for a month." },
      { amount: 50, impact: "$50 pays for a bus-stop poster for two weeks." },
      { amount: 100, impact: "$100 covers about one day of a highway billboard." },
    ],
  },

  // PLACEHOLDER stories (not real people). Replace with real ones, shared with permission,
  // then remove "placeholder: true".
  stories: [
    { quote: "A real story from someone living with heart failure will go here, shared with their permission.", name: "Real story coming soon", role: "Heart failure", placeholder: true },
    { quote: "A real story from someone diagnosed with FMD or SCAD will go here, shared with their permission.", name: "Real story coming soon", role: "FMD and SCAD", placeholder: true },
  ],

  // PLACEHOLDER team. Replace names, roles and add photos (photo: "assets/team/name.jpg"),
  // then remove "placeholder: true" from each real person.
  team: [
    { name: "Founder name", role: "Co-founder", placeholder: true },
    { name: "Founder name", role: "Co-founder", placeholder: true },
  ],

};
