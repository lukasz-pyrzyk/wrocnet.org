---
title: "Wystąpili u nas"
layout: single
permalink: /wystapili-u-nas/
excerpt: "Prelegenci, którzy wystąpili na spotkaniach Wrocławskiej Grupy .NET."
classes: wide
---

{% assign rendered_speaker_ids = "" | split: "" %}
{% assign total_sessions = 0 %}
{% for post in site.posts %}
  {% assign total_sessions = total_sessions | plus: post.talks.size %}
{% endfor %}
<section class="speakers-summary" aria-labelledby="speakers-summary-title">
  <div class="speakers-summary__intro">
    <p class="speakers-summary__eyebrow">Wroc.NET w liczbach</p>
    <h2 id="speakers-summary-title">Ludzie i idee, które budują naszą społeczność.</h2>
  </div>
  <div class="speakers-summary__stats">
    <div class="speakers-summary__stat"><strong>{{ site.data.speakers.size }}</strong><span>prelegentów</span></div>
    <div class="speakers-summary__stat"><strong>{{ total_sessions }}</strong><span>sesji</span></div>
  </div>
</section>

<div class="speakers-toolbar">
  <label class="speaker-search" for="speaker-search-input">
    <span class="speaker-search__label">Znajdź prelegenta</span>
    <span class="speaker-search__field">
      <i class="fas fa-search" aria-hidden="true"></i>
      <input id="speaker-search-input" type="search" placeholder="Imię lub nazwisko" autocomplete="off">
    </span>
  </label>
  <div class="speakers-toolbar__controls">
    <label class="speaker-filter" for="speaker-count-filter">
      <span class="speaker-filter__label">Liczba wystąpień</span>
      <select id="speaker-count-filter">
        <option value="all">Wszystkie</option>
        <option value="1">1 sesja</option>
        <option value="2">2 sesje</option>
        <option value="3">3 sesje</option>
        <option value="4+">4 i więcej</option>
      </select>
    </label>
    <label class="speaker-sort" for="speaker-sort-select">
      <span class="speaker-sort__label">Sortuj wg ostatniego wystąpienia</span>
      <select id="speaker-sort-select">
        <option value="date-desc">Od najnowszych</option>
        <option value="date-asc">Od najstarszych</option>
      </select>
    </label>
    <span id="speaker-search-status" class="speaker-search__status" aria-live="polite"></span>
  </div>
</div>

<div class="speakers-grid">
{% for post in site.posts %}
  {% for talk in post.talks %}
    {% for speaker_id in talk.speaker_ids %}
      {% unless rendered_speaker_ids contains speaker_id %}
        {% assign speaker = site.data.speakers | where: "id", speaker_id | first %}
        {% assign speaker_appearance_count = 0 %}
        {% capture speaker_appearances_html %}
        {% for appearance_post in site.posts %}
          {% for appearance_talk in appearance_post.talks %}
            {% if appearance_talk.speaker_ids contains speaker.id %}
              {% assign speaker_appearance_count = speaker_appearance_count | plus: 1 %}
              <li>
                <a href="{{ appearance_post.url }}">{{ appearance_post.date | date: "%d.%m.%Y" }}</a>
                <span>{{ appearance_talk.title }}</span>
              </li>
            {% endif %}
          {% endfor %}
        {% endfor %}
        {% endcapture %}
  <div class="speaker-card" id="speaker-{{ speaker.id }}" data-speaker-name="{{ speaker.imie }} {{ speaker.nazwisko | downcase }}" data-appearance-count="{{ speaker_appearance_count }}" data-last-date="{{ post.date | date: '%s' }}">
    <div class="speaker-info">
      <h3 class="speaker-name">
        {% if speaker.link %}<a href="{{ speaker.link }}" target="_blank" rel="noopener noreferrer">{{ speaker.imie }} {{ speaker.nazwisko }}</a>{% else %}{{ speaker.imie }} {{ speaker.nazwisko }}{% endif %}
      </h3>
      <ul class="speaker-appearances">{{ speaker_appearances_html }}</ul>
    </div>
  </div>
        {% assign rendered_speaker_ids = rendered_speaker_ids | push: speaker_id %}
      {% endunless %}
    {% endfor %}
  {% endfor %}
{% endfor %}
</div>

<script>
  (() => {
    const speakerSearch = document.getElementById('speaker-search-input');
    const countFilter = document.getElementById('speaker-count-filter');
    const sortSelect = document.getElementById('speaker-sort-select');
    const searchStatus = document.getElementById('speaker-search-status');
    const speakersGrid = document.querySelector('.speakers-grid');
    const speakerCards = Array.from(document.querySelectorAll('.speaker-card'));
    const normalize = (value) => value.trim().toLocaleLowerCase();

    const applyFilters = () => {
      const query = normalize(speakerSearch.value);
      const countValue = countFilter.value;
      const visibleCards = [];

      speakerCards.forEach((card) => {
        const nameMatches = query === '' || normalize(card.dataset.speakerName || '').includes(query);
        const count = Number(card.dataset.appearanceCount || 0);
        const countMatches = countValue === 'all' || (countValue === '4+' ? count >= 4 : count === Number(countValue));
        const visible = nameMatches && countMatches;
        card.hidden = !visible;
        if (visible) visibleCards.push(card);
      });

      searchStatus.textContent = (query !== '' || countValue !== 'all') ? `${visibleCards.length} wyników` : '';

      if (query !== '' && visibleCards.length > 0) {
        const speakerId = visibleCards[0].id;
        window.history.replaceState(null, '', `#${speakerId}`);
        visibleCards[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    };

    const applySort = () => {
      const order = sortSelect.value;
      const sorted = [...speakerCards].sort((a, b) => {
        const dateA = Number(a.dataset.lastDate || 0);
        const dateB = Number(b.dataset.lastDate || 0);
        return order === 'date-asc' ? dateA - dateB : dateB - dateA;
      });
      sorted.forEach((card) => speakersGrid.appendChild(card));
    };

    speakerSearch.addEventListener('input', applyFilters);
    countFilter.addEventListener('change', applyFilters);
    sortSelect.addEventListener('change', applySort);

    applySort();
    applyFilters();
  })();
</script>

<style>
.speakers-summary {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 2.5rem;
  align-items: center;
  margin: 1rem 0 2rem;
  padding: 1.5rem 2rem;
  border-left: 5px solid #641e78;
}
.speakers-summary__eyebrow {
  margin: 0 0 0.35rem;
  color: #641e78;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.speakers-summary h2 {
  max-width: 720px;
  margin: 0;
  color: #1e1428;
  font-size: 1.45rem;
  line-height: 1.25;
}
.speakers-summary__stats {
  display: flex;
  gap: 1.5rem;
  min-width: 220px;
  padding-left: 1.5rem;
  border-left: 1px solid #d9d0e0;
}
.speakers-summary__stat strong,
.speakers-summary__stat span {
  display: block;
}
.speakers-summary__stat strong {
  color: #641e78;
  font-size: 2.1rem;
  line-height: 1;
}
.speakers-summary__stat span {
  margin-top: 0.35rem;
  color: #6b5f75;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}
.speakers-toolbar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 640px;
  margin: 0 auto 1.75rem;
}
.speakers-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
  margin-top: 0;
}
.speaker-search {
  display: block;
  width: 100%;
  margin: 0;
}
.speakers-toolbar__controls {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem;
}
.speaker-filter,
.speaker-sort {
  display: block;
  margin: 0;
  flex: 1 1 200px;
}
.speaker-filter__label,
.speaker-sort__label {
  display: block;
  margin-bottom: 0.45rem;
  color: #1e1428;
  font-size: 0.8rem;
  font-weight: 700;
}
.speaker-filter select,
.speaker-sort select {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #d9d0e0;
  border-radius: 6px;
  background: #fff;
  color: #1e1428;
  font: inherit;
  font-size: 0.88rem;
}
.speaker-filter select:focus,
.speaker-sort select:focus {
  border-color: #641e78;
  box-shadow: 0 0 0 2px rgba(100, 30, 120, 0.16);
  outline: 0;
}
.speaker-search__label {
  display: block;
  margin-bottom: 0.45rem;
  color: #1e1428;
  font-size: 0.8rem;
  font-weight: 700;
}
.speaker-search__field {
  position: relative;
  display: block;
}
.speaker-search__field i {
  position: absolute;
  top: 50%;
  left: 1.1rem;
  color: #641e78;
  font-size: 0.9rem;
  transform: translateY(-50%);
  pointer-events: none;
}
.speaker-search input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.75rem;
  border: 1px solid #d9d0e0;
  border-radius: 6px;
  background: #fff;
  color: #1e1428;
  font: inherit;
  font-size: 0.88rem;
}
.speaker-search input:focus {
  background: #fff;
  border-color: #641e78;
  box-shadow: 0 0 0 2px rgba(100, 30, 120, 0.16);
  outline: 0;
}
.speaker-search__status {
  display: block;
  flex-basis: 100%;
  min-height: 1rem;
  margin-top: 0.35rem;
  color: #641e78;
  font-size: 0.72rem;
  font-weight: 700;
  text-align: right;
  white-space: nowrap;
}
.speaker-card[hidden] {
  display: none;
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
  .speakers-summary {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1.25rem;
  }

  .speakers-summary h2 {
    font-size: 1.25rem;
  }

  .speakers-summary__stats {
    min-width: 0;
    padding-left: 0;
    border-left: 0;
  }

  .speakers-toolbar {
    flex-direction: column;
    align-items: stretch;
    max-width: none;
    margin-bottom: 1.25rem;
  }

  .speakers-toolbar__controls {
    flex-direction: column;
  }

  .speaker-search__status {
    flex-basis: auto;
  }

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