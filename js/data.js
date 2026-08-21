/**
 * 악군 데이터 로더
 * GitHub Pages의 정적 환경에서 JSON만 읽어 사이트 데이터를 구성합니다.
 */

export const DATA = {
    meta: null,
    items: [],
    uniques: [],
    runewords: [],
    sunders: [],
    charms: [],
    ubers: [],
    builds: [],
    indexes: {
        item: new Map(),
        unique: new Map(),
        runeword: new Map(),
        sunder: new Map(),
        charm: new Map(),
        uber: new Map(),
        build: new Map()
    }
};

let loadPromise = null;

function indexRecords(type, records) {
    const map = DATA.indexes[type];
    map.clear();

    records.forEach(record => {
        map.set(Number(record.id), record);
        if (record.legacyKey) map.set(record.legacyKey, record);
        if (record.name) map.set(record.name, record);
    });
}

export async function loadData() {
    if (loadPromise) return loadPromise;

    const dataVer = "12";
    loadPromise = Promise.all([
        fetch(`./data/meta.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/items.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/uniques.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/runewords.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/sunders.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/charms.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/ubers.json?v=${dataVer}`).then(r => r.json()),
        fetch(`./data/builds.json?v=${dataVer}`).then(r => r.json())
    ]).then(([meta, items, uniques, runewords, sunders, charms, ubers, builds]) => {
        DATA.meta = meta;
        DATA.items = items;
        DATA.uniques = uniques;
        DATA.runewords = runewords;
        DATA.sunders = sunders;
        DATA.charms = charms;
        DATA.ubers = ubers;
        DATA.builds = builds.items ?? builds;

        indexRecords('item', DATA.items);
        indexRecords('unique', DATA.uniques);
        indexRecords('runeword', DATA.runewords);
        indexRecords('sunder', DATA.sunders);
        indexRecords('charm', DATA.charms);
        indexRecords('uber', DATA.ubers);
        indexRecords('build', DATA.builds);

        return DATA;
    }).catch(error => {
        console.error('악군 JSON 데이터를 불러오지 못했습니다.', error);
        loadPromise = null;
        throw error;
    });

    return loadPromise;
}

export function getRecord(type, id) {
    return DATA.indexes[type]?.get(Number(id)) ?? DATA.indexes[type]?.get(id) ?? null;
}
