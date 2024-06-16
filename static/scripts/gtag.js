function gtag(consent, default1, param4) {

}

gtag('consent', 'default', {
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'analytics_storage': 'denied',
    'wait_for_update': 600
});

function allConsentGranted() {
    gtag('consent', 'update', {
        'ad_user_data': 'granted',
        'ad_personalization': 'granted',
        'ad_storage': 'granted',
        'analytics_storage': 'granted'
    });
}
const measurement_id = `G-49D9STDEKG`;
const api_secret = `wMKCSzRbTWCmylcb4o-omg`;

function fetch(){
    let response_from_gtag;
    (`https://www.google-analytics.com/debug/mp/collect?measurement_id=${measurement_id}&api_secret=${api_secret}`, {
    method: "POST",
    body: JSON.stringify({
        client_id: '604768883345-a3pud6hri3772rbn97thb1lp0pvfh2t2.apps.googleusercontent.com',
        events: [{
            // Event names must start with an alphabetic character.
            name: '_badEventName',
            params : {},
        }]
    })
 }).then(r =>{let response_from_gtag;});}

