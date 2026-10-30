import * as CookieConsent from '../vendor/cookieconsent-3.1.0/cookieconsent.esm.js';

const settings = document.getElementById('wrocnet-cookie-consent');
const trackingId = settings.dataset.trackingId;
const analyticsEnabled = settings.dataset.analyticsEnabled === 'true';
let analyticsLoaded = false;

function updateAnalytics() {
  const accepted = CookieConsent.acceptedCategory('analytics');
  window[`ga-disable-${trackingId}`] = !accepted;

  if (!analyticsEnabled || !accepted || analyticsLoaded) return;

  analyticsLoaded = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () {
    window.dataLayer.push(arguments);
  };
  window.gtag('consent', 'default', {
    analytics_storage: 'granted',
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied'
  });
  window.gtag('js', new Date());
  window.gtag('config', trackingId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });

  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(trackingId)}`;
  script.addEventListener('error', () => {
    console.error('Nie udało się załadować Google Analytics.');
  });
  document.head.appendChild(script);
}

await CookieConsent.run({
  mode: 'opt-in',
  hideFromBots: false,
  cookie: {
    name: 'wrocnet_consent',
    expiresAfterDays: 182,
    sameSite: 'Lax'
  },
  guiOptions: {
    consentModal: {
      layout: 'box inline',
      position: 'bottom right',
      equalWeightButtons: true
    },
    preferencesModal: {
      layout: 'box',
      equalWeightButtons: true
    }
  },
  onConsent: updateAnalytics,
  onChange: updateAnalytics,
  categories: {
    necessary: {
      enabled: true,
      readOnly: true
    },
    analytics: {
      autoClear: {
        cookies: [{ name: /^_ga(?:_|$)/ }],
        reloadPage: true
      }
    }
  },
  language: {
    default: 'pl',
    translations: {
      pl: {
        consentModal: {
          title: 'Pomóż nam ulepszać stronę',
          description: 'Za Twoją zgodą użyjemy Google Analytics do pomiaru odwiedzin. Możesz odmówić lub później zmienić decyzję w ustawieniach prywatności w stopce.',
          acceptAllBtn: 'Akceptuję',
          acceptNecessaryBtn: 'Odrzucam',
          showPreferencesBtn: 'Ustawienia prywatności'
        },
        preferencesModal: {
          title: 'Ustawienia prywatności',
          acceptAllBtn: 'Akceptuję',
          acceptNecessaryBtn: 'Odrzucam',
          savePreferencesBtn: 'Zapisz ustawienia',
          closeIconLabel: 'Zamknij',
          serviceCounterLabel: 'Usługi',
          sections: [
            {
              title: 'Twój wybór',
              description: 'Analityka jest dobrowolna. Odmowa nie ogranicza korzystania ze strony. Zgodę możesz wycofać w dowolnym momencie, otwierając te ustawienia w stopce.'
            },
            {
              title: 'Niezbędne',
              description: 'Plik wrocnet_consent zapamiętuje Twoją decyzję przez 182 dni. Nie służy do śledzenia odwiedzin.',
              linkedCategory: 'necessary'
            },
            {
              title: 'Analityka — Google Analytics',
              description: 'Po akceptacji Google Analytics 4 otrzymuje dane o odwiedzanych stronach i korzystaniu z witryny oraz zapisuje pliki _ga i _ga_…. Przed zgodą nie łączymy się z Google w celu analityki. Wycofanie zgody usuwa te pliki i odświeża stronę, aby zatrzymać analitykę. Więcej: <a href="https://policies.google.com/privacy?hl=pl" target="_blank" rel="noopener noreferrer">polityka prywatności Google</a>.',
              linkedCategory: 'analytics'
            }
          ]
        }
      }
    }
  }
});

document.getElementById('cookie-preferences').hidden = false;
