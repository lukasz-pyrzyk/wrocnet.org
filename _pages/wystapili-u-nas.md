---
title: "Wystąpili u nas"
layout: single
permalink: /wystapili-u-nas/
excerpt: "Prelegenci, którzy wystąpili na spotkaniach Wrocławskiej Grupy .NET."
classes: wide
---

{% assign rendered_speaker_ids = "" | split: "" %}
<div class="speakers-grid">
{% for post in site.posts %}
  {% for talk in post.talks %}
    {% for speaker_id in talk.speaker_ids %}
      {% unless rendered_speaker_ids contains speaker_id %}
        {% assign speaker = site.data.speakers | where: "id", speaker_id | first %}
  <div class="speaker-card">
    <div class="speaker-info">
      <h3 class="speaker-name">
        {% if speaker.link %}<a href="{{ speaker.link }}" target="_blank" rel="noopener noreferrer">{{ speaker.imie }} {{ speaker.nazwisko }}</a>{% else %}{{ speaker.imie }} {{ speaker.nazwisko }}{% endif %}
      </h3>
      <ul class="speaker-appearances">
      {% for appearance_post in site.posts %}
        {% for appearance_talk in appearance_post.talks %}
          {% if appearance_talk.speaker_ids contains speaker.id %}
            <li>
              <a href="{{ appearance_post.url }}">{{ appearance_post.date | date: "%d.%m.%Y" }}</a>
              <span>{{ appearance_talk.title }}</span>
            </li>
          {% endif %}
        {% endfor %}
      {% endfor %}
      </ul>
    </div>
  </div>
        {% assign rendered_speaker_ids = rendered_speaker_ids | push: speaker_id %}
      {% endunless %}
    {% endfor %}
  {% endfor %}
{% endfor %}
</div>

<style>
.speakers-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}
.speaker-card {
  display: flex;
  min-height: 150px;
  padding: 1.75rem;
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
.speaker-appearances {
  margin: 0;
  padding-left: 1.1rem;
}
.speaker-appearances li {
  margin-bottom: 0.7rem;
  font-size: 0.88em;
}
.speaker-appearances a {
  display: block;
  color: #641e78;
  font-weight: 700;
  font-size: 0.82em;
}
.speaker-appearances span {
  display: block;
  margin-top: 0.15rem;
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
    padding: 1.25rem;
  }
}
</style>