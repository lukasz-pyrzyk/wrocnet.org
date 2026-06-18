---
title: "Mentorzy"
layout: single
permalink: /mentorzy/
author_profile: true
classes: wide
---

Na nasze spotkania przychodzi wiele młodych osób, które dopiero zaczynają karierę programisty lub szukają pomocnej dłoni przy codziennych wyzwaniach. Często są to pytania o kierunek rozwoju, zmianę pracy, przełamanie stagnacji albo konkretne problemy techniczne.

**Oferujemy mentoring** – możliwość regularnych rozmów z jednym z naszych mentorów. Bezpłatnie, bez zobowiązań.

Masz pytanie lub chcesz porozmawiać? Skontaktuj się bezpośrednio przez LinkedIn lub zagadaj na spotkaniu :)

<div class="organizers-grid">
{% for person in site.data.mentors %}
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
      {% if person.blog %}
        <a href="{{ person.blog }}" target="_blank" rel="noopener noreferrer" class="btn btn--inverse btn--small" style="margin-top: 0.4rem;">
          <i class="fas fa-blog"></i> Blog
        </a>
      {% endif %}
    </div>
  </div>
{% endfor %}
</div>

<style>
.organizers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  margin-top: 2rem;
}
@media (max-width: 900px) { .organizers-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .organizers-grid { grid-template-columns: 1fr; } }
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
.organizer-info .btn {
  width: auto;
}
</style>
