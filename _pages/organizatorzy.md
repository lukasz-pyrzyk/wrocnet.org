---
title: "Organizatorzy"
layout: single
permalink: /organizatorzy/
classes: wide
---

<div class="organizers-grid">
{% for person in site.data.organizers %}{% if person.name and person.name != "" %}
  <div class="organizer-card">
    <img src="{{ person.photo | default: '/assets/images/organizers/placeholder.png' }}" alt="{{ person.name }}" class="organizer-photo">
    <div class="organizer-info">
      <h3 class="organizer-name">{{ person.name }}</h3>
      {% if person.bio and person.bio != "" %}<p class="organizer-bio">{{ person.bio }}</p>{% endif %}
      {% if person.linkedin %}
        <a href="{{ person.linkedin }}" target="_blank" rel="noopener noreferrer" class="btn btn--primary btn--small">
          <i class="fab fa-linkedin"></i> LinkedIn
        </a>
      {% endif %}
    </div>
  </div>
{% endif %}{% endfor %}
</div>

{% if site.data.former_organizers and site.data.former_organizers.size > 0 %}
<h2 class="former-organizers-heading">Byli organizatorzy</h2>
<div class="organizers-grid organizers-grid--former">
{% for person in site.data.former_organizers %}
  <div class="organizer-card organizer-card--former">
    <img src="{{ person.photo | default: '/assets/images/organizers/placeholder.png' }}" alt="{{ person.name }}" class="organizer-photo organizer-photo--former">
    <div class="organizer-info">
      <h3 class="organizer-name">{{ person.name }}</h3>
      {% if person.bio and person.bio != "" %}<p class="organizer-bio">{{ person.bio }}</p>{% endif %}
      {% if person.linkedin %}
        <a href="{{ person.linkedin }}" target="_blank" rel="noopener noreferrer" class="btn btn--inverse btn--small">
          <i class="fab fa-linkedin"></i> LinkedIn
        </a>
      {% endif %}
    </div>
  </div>
{% endfor %}
</div>
{% endif %}

<style>
.organizers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  margin-top: 1.5rem;
}
.organizer-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.5rem;
  border: 1px solid #e0d5e8;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(100, 30, 120, 0.08);
}
.organizer-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  width: 100%;
}
.organizer-info .btn {
  margin-top: auto;
  align-self: center;
  width: auto;
}
.organizer-photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #641e78;
  margin-bottom: 1rem;
}
.organizer-name {
  margin: 0 0 0.5rem;
  color: #641e78;
}
.organizer-bio {
  font-size: 0.9em;
  color: #555;
  margin-bottom: 1rem;
}
.former-organizers-heading {
  margin-top: 3rem;
  color: #555;
  font-size: 1.2em;
  border-top: 1px solid #e0d5e8;
  padding-top: 2rem;
}
.organizer-photo--former {
  border-color: #aaa;
  filter: grayscale(40%);
}
.organizer-card--former {
  opacity: 0.8;
  border-color: #ccc;
}
</style>
