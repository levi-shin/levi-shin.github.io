/**
 * 사이트 공통 설정 (언어·절대 경로·UI 문자열)
 * /en/ 하위에서도 /data, /items, /css, /js 루트 자산을 쓰도록 합니다.
 */

export const SITE_ORIGIN = 'https://diablo.1125labs.com';

/** EN 전용 JSON이 있는 파일 */
const LOCALIZED_DATA_FILES = new Set([
    'uniques.json',
    'runewords.json',
    'runes.json',
    'builds.json',
    'leveling.json',
    'dropcalc.json',
    'patchnotes.json',
    'sunders.json',
    'charms.json',
    'ubers.json',
    'meta.json'
]);

function detectLang() {
    if (typeof document === 'undefined') {
        return 'ko';
    }
    const htmlLang = (document.documentElement.lang || '').toLowerCase();
    if (htmlLang.startsWith('en')) return 'en';
    if (htmlLang.startsWith('ko')) return 'ko';
    if (typeof location !== 'undefined' && location.pathname.startsWith('/en')) return 'en';
    return 'ko';
}

export const SITE_LANG = detectLang();
export const SITE_HOME = SITE_LANG === 'en' ? '/en/' : '/';
export const SITE_ALT_HOME = SITE_LANG === 'en' ? '/' : '/en/';

const UI = {
    ko: {
        ladderOnly: '🔥 래더 전용',
        ladderOk: '✨ 비래더가능',
        runeTier: { high: '고급 룬', mid: '중급 룬', low: '하급 룬' },
        runeNum: (n) => `${n}번`,
        searchEmpty: '검색 결과가 없습니다.',
        searchHeader: (keyword) => `🔍 '${keyword}' 통합 검색 결과`,
        searchBuilds: '🛡️ 추천 종결 빌드',
        searchBuildBadge: '종결 빌드',
        searchRelated: '🛡️ 연관 사용처 (종결 빌드 세팅)',
        copyBuildOk: '종결 빌드 및 용병 세팅 정보가 클립보드에 복사되었습니다!',
        copyUnsupported: '복사하기 기능이 지원되지 않는 브라우저입니다.',
        copyInfoOk: '정보를 클립보드에 복사했습니다!',
        copyRecipeOk: (recipe) => `조합 순서를 복사했습니다.\n${recipe}`,
        copyRecipeFallback: (recipe) => `조합 순서: ${recipe}`,
        copyPaperOk: '빌드 정보가 복사되었습니다!',
        paperDefaultTitle: '빌드 정보',
        patchLinkTitle: '공식 패치 노트 원문 보기',
        patchSchedule: '📅 시즌 일정',
        patchChanges: '📝 주요 변경 사항',
        leveling: {
            classHead: '직업별 시즌 초 운영',
            runeHead: '만들 순서 (룬어)',
            runeCols: ['룬어', '구간', '왜 만드나'],
            countessHead: '카운테스 룬 구간',
            countessCols: ['난이도', '드랍 룬', '쓰임'],
            socketHead: '라주크 소켓은 아껴 두세요',
            socketCols: ['난이도', '권장 사용'],
            tipsHead: '놓치기 쉬운 점',
            buildBtn: '종결 세팅 보기',
            mercCols: ['구간', '고용', '무기', '갑옷', '투구'],
            footerNote: '버스는 <span class="item-inline" onclick="switchSection(null, \'bus\')">11. 버스 가이드</span>, 퀘스트 보상은 <span class="item-inline" onclick="switchSection(null, \'quest\')">10. 영구보상 퀘스트</span>, 용병은 <span class="item-inline" onclick="switchSection(null, \'merc\')">8. 용병 세팅</span>을 이어서 보시면 됩니다.'
        },
        feedback: {
            limit: (n) => `⚠️ 오늘의 제보 한도(${n}회)를 모두 사용하셨습니다.\n내일 자정 이후 다시 제보해 주세요. 감사합니다!`,
            ok: (type, remaining) => `[${type}] 제보가 정상 수신되었습니다! (오늘 남은 제보 횟수: ${remaining}회)\n소중한 의견 감사합니다.`,
            slackTitle: (next, max) => `📢 *[디아2 백과사전] 새로운 제보/피드백이 접수되었습니다! (오늘 유저 제보 ${next}/${max}회)*`,
            nick: '👤 닉네임',
            anon: '익명',
            type: '📌 제보 유형',
            time: '⏰ 접수 시간',
            detail: '📝 상세 내용',
            langTag: 'ko'
        },
        dropcalc: {
            perKill: (farm, mult) => `${farm} · per kill · ${mult.toFixed(2)}x vs 0 MF`,
            empty: '검색하신 아이템이 목록에 없습니다.',
            inputMf: '입력 매찬',
            uniqMf: '유니크 유효 매찬',
            setMf: '세트 유효 매찬',
            rareMf: '레어 유효 매찬',
            feel: (m) => `체감 ${m.toFixed(2)}배`,
            heading: '유니크 드랍 확률',
            cols: ['아이템', '현재 확률', '퍼센트', '절반 확률', '0매찬'],
            half: (n) => `약 ${n}회`,
            loadFail: '계산 데이터를 불러오지 못했습니다. 잠시 후 다시 눌러 주세요.'
        },
        runeModal: {
            subtitle: (eng, name) => `룬어 · ${eng || name}`,
            intro: '룬 조합 순서와 추천 종결 베이스, 그리고 으뜸 수치를 확인합니다.',
            ladder: '래더 여부',
            recipe: '룬 조합 순서',
            base: '종결 권장 베이스',
            stats: '으뜸(최상급) 변동 옵션',
            copy: '📋 룬 조합 복사'
        },
        uniqueModal: {
            subtitle: (eng) => `유니크 · ${eng || 'Unique Item'}`,
            intro: '유니크 아이템의 최상급(으뜸) 옵션 정보입니다.',
            base: '아이템 종류 / 베이스',
            drop: '대표 드랍 장소',
            dropEmpty: '정보 없음',
            stats: '으뜸(최상급) 옵션 스펙',
            copy: '📋 아이템 정보 복사'
        },
        copyGeneric: '📋 정보 복사',
        copyCube: '📋 큐빙 공식 복사',
        searchPrimary: '✨ 핵심 정보 (조합 및 스펙)',
        searchCat: {
            runeword: '룬어 조합식',
            unique: '유니크 아이템',
            sunder: '신 파괴참',
            charm: '종결 부적',
            uber: '우버 바바/주얼',
            leveling: '육성 가이드'
        },
        searchHighlight: {
            recipe: (v) => `조합: ${v}`,
            base: (v) => `베이스: ${v}`,
            drop: (v) => `드랍: ${v}`,
            obtain: (v) => `획득: ${v}`,
            summon: (v) => `소환/효과: ${v}`,
            leveling: '노말부터 지옥 자립 순서'
        },
        sunderModal: {
            subtitle: (key) => `신 파괴참 · ${key} 속성`,
            intro: (drop) => `드랍 장소: ${drop}`,
            recipe: '업그레이드 큐빙 공식 (호라드림의 함)',
            stats: '새로워진 파괴참 상세 스펙',
            copyPrefix: (name) => `${name} 공식`
        },
        charmModal: {
            subtitle: '종결 부적 정보',
            intro: (drop) => `획득 방법: ${drop}`,
            stats: '부적 고유 옵션 스펙'
        },
        uberModal: {
            subtitle: '우버 바바 · 전용 주얼 족보',
            stats: '드랍 주얼 및 부적 상세 스펙',
            copySuffix: '드랍 보상 스펙 정보'
        },
        buildGuide: {
            stats: '📊 스탯',
            inventory: '🎒 인벤토리',
            skills: '⚡ 스킬',
            playstyle: '🎮 운영법'
        },
        buildCard: {
            clickHint: '클릭하여 상세 장비 세팅을 확인하세요.',
            viewSlots: '장비 슬롯 보기'
        },
        ladderOnlyShort: '래더전용'
    },
    en: {
        ladderOnly: '🔥 Ladder only',
        ladderOk: '✨ Non-ladder OK',
        runeTier: { high: 'High', mid: 'Mid', low: 'Low' },
        runeNum: (n) => `#${n}`,
        searchEmpty: 'No results.',
        searchHeader: (keyword) => `🔍 Results for '${keyword}'`,
        searchBuilds: '🛡️ Suggested endgame builds',
        searchBuildBadge: 'Endgame',
        searchRelated: '🛡️ Used in endgame builds',
        copyBuildOk: 'Build & mercenary setup copied to clipboard!',
        copyUnsupported: 'Clipboard copy is not supported in this browser.',
        copyInfoOk: 'Copied to clipboard!',
        copyRecipeOk: (recipe) => `Copied rune order.\n${recipe}`,
        copyRecipeFallback: (recipe) => `Rune order: ${recipe}`,
        copyPaperOk: 'Build info copied!',
        paperDefaultTitle: 'Build info',
        patchLinkTitle: 'Open official patch notes',
        patchSchedule: '📅 Season schedule',
        patchChanges: '📝 Highlights',
        leveling: {
            classHead: 'Early season by class',
            runeHead: 'Craft order (runewords)',
            runeCols: ['Runeword', 'When', 'Why'],
            countessHead: 'Countess rune tiers',
            countessCols: ['Difficulty', 'Runes', 'Use'],
            socketHead: 'Save Larzuk sockets',
            socketCols: ['Difficulty', 'Recommended use'],
            tipsHead: 'Easy to miss',
            buildBtn: 'View endgame setup',
            mercCols: ['Stage', 'Hire', 'Weapon', 'Armor', 'Helm'],
            footerNote: 'Continue with <span class="item-inline" onclick="switchSection(null, \'bus\')">11. Bus Guide</span>, <span class="item-inline" onclick="switchSection(null, \'quest\')">10. Permanent Quests</span>, and <span class="item-inline" onclick="switchSection(null, \'merc\')">8. Mercenary Setups</span>.'
        },
        feedback: {
            limit: (n) => `⚠️ Daily report limit (${n}) used.\nPlease try again after midnight. Thanks!`,
            ok: (type, remaining) => `[${type}] Report received! (Remaining today: ${remaining})\nThank you.`,
            slackTitle: (next, max) => `📢 *[D2 Encyclopedia] New feedback (${next}/${max} today)*`,
            nick: '👤 Nickname',
            anon: 'Anonymous',
            type: '📌 Type',
            time: '⏰ Time',
            detail: '📝 Details',
            langTag: 'en'
        },
        dropcalc: {
            perKill: (farm, mult) => `${farm} · per kill · ${mult.toFixed(2)}x vs 0 MF`,
            empty: 'No matching items in the list.',
            inputMf: 'Your MF',
            uniqMf: 'Unique effective MF',
            setMf: 'Set effective MF',
            rareMf: 'Rare effective MF',
            feel: (m) => `${m.toFixed(2)}x feel`,
            heading: 'Unique drop odds',
            cols: ['Item', 'Odds now', 'Percent', '50% chance', '0 MF'],
            half: (n) => `~${n} kills`,
            loadFail: 'Could not load calculator data. Try again shortly.'
        },
        runeModal: {
            subtitle: (eng, name) => `Runeword · ${eng || name}`,
            intro: 'Rune order, recommended endgame bases, and perfect rolls.',
            ladder: 'Ladder',
            recipe: 'Rune order',
            base: 'Recommended base',
            stats: 'Perfect / variable mods',
            copy: '📋 Copy rune order'
        },
        uniqueModal: {
            subtitle: (eng) => `Unique · ${eng || 'Unique Item'}`,
            intro: 'Perfect-roll unique item details.',
            base: 'Item type / base',
            drop: 'Notable drop sources',
            dropEmpty: 'No data',
            stats: 'Perfect mods',
            copy: '📋 Copy item info'
        },
        copyGeneric: '📋 Copy info',
        copyCube: '📋 Copy cube recipe',
        searchPrimary: '✨ Key info (recipes & specs)',
        searchCat: {
            runeword: 'Runeword',
            unique: 'Unique',
            sunder: 'Sunder Charm',
            charm: 'Endgame charm',
            uber: 'Uber Barb / Jewel',
            leveling: 'Leveling guide'
        },
        searchHighlight: {
            recipe: (v) => `Recipe: ${v}`,
            base: (v) => `Base: ${v}`,
            drop: (v) => `Drop: ${v}`,
            obtain: (v) => `Obtain: ${v}`,
            summon: (v) => `Summon: ${v}`,
            leveling: 'Normal through Hell progression'
        },
        sunderModal: {
            subtitle: (key) => `Sunder Charm · ${key}`,
            intro: (drop) => `Drop zone: ${drop}`,
            recipe: 'Upgrade cube recipe (Horadric Cube)',
            stats: 'Upgraded Sunder Charm stats',
            copyPrefix: (name) => `${name} recipe`
        },
        charmModal: {
            subtitle: 'Endgame charm',
            intro: (drop) => `How to obtain: ${drop}`,
            stats: 'Charm mods'
        },
        uberModal: {
            subtitle: 'Uber Barb · exclusive jewels',
            stats: 'Jewel & charm drop specs',
            copySuffix: 'drop reward specs'
        },
        buildGuide: {
            stats: '📊 Stats',
            inventory: '🎒 Inventory',
            skills: '⚡ Skills',
            playstyle: '🎮 Playstyle'
        },
        buildCard: {
            clickHint: 'Click to view the full gear setup.',
            viewSlots: 'View gear slots'
        },
        ladderOnlyShort: 'Ladder only'
    }
};

export function t() {
    return UI[SITE_LANG] || UI.ko;
}

export function assetUrl(path) {
    const clean = String(path || '').replace(/^\.\//, '').replace(/^\//, '');
    return `/${clean}`;
}

export function dataUrl(file, ver) {
    const name = String(file || '').replace(/^\.?\/*data\//, '').replace(/^en\//, '');
    const q = ver != null && ver !== '' ? `?v=${ver}` : '';
    if (SITE_LANG === 'en' && LOCALIZED_DATA_FILES.has(name)) {
        return `/data/en/${name}${q}`;
    }
    return `/data/${name}${q}`;
}

export function itemImageUrl(imagePath) {
    if (!imagePath) return '';
    return assetUrl(`items/${imagePath}`);
}

/**
 * Optional: archive feedback to repo JSON via repository_dispatch.
 * Set patParts + secretParts (match secrets.FEEDBACK_SUBMIT_SECRET).
 * Slack webhook is server-side only (secrets.SLACK_WEBHOOK_URL in GHA).
 */
export const FEEDBACK_GITHUB = {
    repo: 'levi-shin/levi-shin.github.io',
    patParts: ['ghs_1210556_eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJhdXRobmQiLCJjdHgiOiJxbEdHSHJ3bFRSc2FSa2Npdk8zQ1FmcEVkZ29HRDRDSmpVRU1DS', '0NmVUMzUnR5bTlHcEhRNTJPc3ZJaElObGciLCJleHAiOjE3ODgzMTA4NjIsImlhdCI6MTc4ODMwNzI2MiwiaXNzIjoiZ2l0aHViIiwianRpIjoiMTY4NzdhYmItYTE4Yy0', '0MDcwLTg0MTctZWVlZDkyY2ZhNWM2IiwidmVyIjozfQ.WJJ8Kk8KRmd-xsLfWp9xzIJfjFzDIPbyiZfUX2TCLVq9qqVGPqkClkljZzo15JrImpKzkYDombCCxYMMnYi5XQ'],
    secretParts: ['2c61a8a3fb136c6077463c46', '6a150ca2f21c718ecbdb0d3e']
};

export function submitFeedbackArchive({ nick, type, content, lang }) {
    const token = FEEDBACK_GITHUB.patParts.join('');
    const secret = FEEDBACK_GITHUB.secretParts.join('');
    if (!token || !secret) return;

    const body = {
        event_type: 'feedback',
        client_payload: {
            secret,
            nick: nick || '',
            nickname: nick || '',
            type: type || 'Other',
            content: content || '',
            lang: lang || SITE_LANG,
            source: 'web'
        }
    };

    fetch(`https://api.github.com/repos/${FEEDBACK_GITHUB.repo}/dispatches`, {
        method: 'POST',
        headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/vnd.github+json',
            'Content-Type': 'application/json',
            'X-GitHub-Api-Version': '2022-11-28'
        },
        body: JSON.stringify(body)
    }).catch(() => {});
}

if (typeof window !== 'undefined') {
    window.SITE_LANG = SITE_LANG;
    window.SITE_HOME = SITE_HOME;
    window.SITE_ORIGIN = SITE_ORIGIN;
}
