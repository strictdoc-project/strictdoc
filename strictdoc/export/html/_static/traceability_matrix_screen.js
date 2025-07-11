// @relation(SDOC-SRS-112, scope=file)

const SELECTOR = '[js-requirements-coverage]';

const __log = (topic, ...payload) => {
  console.log(`%c ${topic} `, 'background:yellow;color:black',
    ...payload
  );
}

function markSame(newUid, state, arr) {
  // __log('state', state.currentUid);
  state.currentUid && arr[state.currentUid].forEach(element => element.classList.remove('highlighted'));
  state.currentUid = newUid;
  arr[newUid].forEach(element => element.classList.add('highlighted'));

}

window.addEventListener("load", function () {
  // __log(
  //   'requirements-coverage',
  //   'test'
  // )

  const state = {
    currentUid: null
  }

  // https://stackoverflow.com/questions/32249997/how-to-check-if-data-attribute-exist-with-plain-javascript/32250073
  const reqs = [...document.querySelectorAll(SELECTOR)]
    .reduce((acc, req) => {
      if (req.hasAttribute('data-uid')) {
        req.addEventListener('click', () => markSame(uid, state, reqs));
        const uid = req.dataset.uid;
        acc[uid] = acc[uid] ? [...acc[uid], req] : [req];
      } else {
        req.classList.add('nouid')
        acc.nouid.push(req);
      }
      return acc
    }, { nouid: [] });

  // __log(
  //   '--',
  //   reqs
  // )

});
