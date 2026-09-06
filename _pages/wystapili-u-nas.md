---
title: "Wystąpili u nas"
layout: single
permalink: /wystapili-u-nas/
excerpt: "Prelegenci, którzy wystąpili na spotkaniach Wrocławskiej Grupy .NET."
classes: wide
---

{% assign speakers = site.data.speakers | sort: "ostatnie_wystapienie" | reverse %}
<div class="speakers-grid">
{% for speaker in speakers %}
  <div class="speaker-card">
    <div class="speaker-info">
      <h3 class="speaker-name">
        {% if speaker.link %}<a href="{{ speaker.link }}" target="_blank" rel="noopener noreferrer">{{ speaker.imie }} {{ speaker.nazwisko }}</a>{% else %}{{ speaker.imie }} {{ speaker.nazwisko }}{% endif %}
      </h3>
      <p class="speaker-last-talk">Ostatnie wystąpienie: {{ speaker.ostatnie_wystapienie | date: "%d.%m.%Y" }}</p>
      <a href="{{ speaker.ostatni_post }}" class="btn btn--primary btn--small">Ostatnia prelekcja</a>
    </div>
  </div>
{% endfor %}
</div>

<style>
.speakers-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 2rem;
  margin-top: 1.5rem;
}
.speaker-card {
  display: flex;
  min-height: 150px;
  padding: 1.5rem;
  border: 1px solid #e0d5e8;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(100, 30, 120, 0.08);
}
.speaker-info {
  display: flex;
  flex-direction: column;
  width: 100%;
}
.speaker-name {
  margin: 0 0 0.5rem;
  color: #641e78;
  word-wrap: break-word;
}
.speaker-name a {
  color: inherit;
}
.speaker-last-talk {
  margin: 0 0 1rem;
  color: #555;
  font-size: 0.9em;
}
.speaker-info .btn {
  align-self: flex-start;
  margin-top: auto;
}

@media (max-width: 1024px) {
  .speakers-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.25rem;
  }
}

@media (max-width: 640px) {
  .speakers-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .speaker-card {
    min-height: 0;
    padding: 1rem;
  }
}
</style>