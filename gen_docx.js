const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, AlignmentType, BorderStyle, WidthType, ShadingType,
  VerticalAlign, PageBreak, LevelFormat, LineRuleType
} = require('docx');
const fs = require('fs');

const C = {
  navy:'191970', gold:'FFCB05', goldDark:'B8860B',
  green:'2EC484', greenDk:'1A7A50', red:'FF6432', redDk:'CC3300',
  purple:'6B3FA0',
  gray:'E6E9EF', bgBlue:'EEF0FA', bgYellow:'FFFBE6',
  bgGreen:'EDFAF3', bgRed:'FFF3EE',
  white:'FFFFFF', text:'1A1A2E', sub:'666688', light:'F8F9FF',
};
const W = 9026;
const bd  = (c='CCCCCC',s=6) => ({ style: BorderStyle.SINGLE, size:s, color:c });
const bds = (c='CCCCCC')     => ({ top:bd(c), bottom:bd(c), left:bd(c), right:bd(c) });
const noBd  = { style: BorderStyle.NIL };
const noBds = { top:noBd, bottom:noBd, left:noBd, right:noBd };

function gap(pts=120) {
  return new Paragraph({ spacing:{ before:pts, after:0 }, children:[] });
}
function heading(text, level=1) {
  const sz = level===1?28:level===2?22:19;
  const cl = level===1?C.navy:level===2?C.navy:C.sub;
  return new Paragraph({
    spacing:{ before:level===1?320:180, after:80 },
    border: level===1 ? { bottom:{ style:BorderStyle.SINGLE, size:8, color:C.gold } } : {},
    children:[new TextRun({ text, font:'Arial', size:sz, bold:true, color:cl })]
  });
}
function para(text, opts={}) {
  return new Paragraph({
    spacing:{ line:360, lineRule:LineRuleType.AUTO, before:40, after:40 },
    children:[new TextRun({ text:text||'', font:'Arial', size:20, color:C.text, ...opts })]
  });
}
function kv(label, value) {
  return new Paragraph({
    spacing:{ line:340, lineRule:LineRuleType.AUTO, before:40, after:40 },
    children:[
      new TextRun({ text:label+'  ', font:'Arial', size:20, bold:true, color:C.navy }),
      new TextRun({ text:String(value||'-'), font:'Arial', size:20, color:C.text }),
    ]
  });
}
function divider() {
  return new Paragraph({
    spacing:{ before:200, after:0 },
    border:{ bottom:{ style:BorderStyle.SINGLE, size:4, color:C.gray } },
    children:[]
  });
}
function colorBox({ label='', text='', bg=C.bgBlue, borderColor=C.navy, borderSize=14 }) {
  const rows = [];
  if (label) rows.push(new Paragraph({
    spacing:{ after:60 },
    children:[new TextRun({ text:label, font:'Arial', size:17, bold:true, color:borderColor })]
  }));
  (text||'-').split('\n').forEach(line => {
    rows.push(new Paragraph({
      spacing:{ line:340, lineRule:LineRuleType.AUTO, before:20, after:20 },
      children:[new TextRun({ text:line||'', font:'Arial', size:19, color:C.text })]
    }));
  });
  return new Table({
    width:{ size:W, type:WidthType.DXA }, columnWidths:[W],
    rows:[new TableRow({ children:[new TableCell({
      borders:{ top:bd(borderColor,4), bottom:bd(borderColor,4), right:bd(borderColor,4),
                left:{ style:BorderStyle.SINGLE, size:borderSize, color:borderColor } },
      shading:{ fill:bg, type:ShadingType.CLEAR },
      margins:{ top:120, bottom:120, left:200, right:200 },
      width:{ size:W, type:WidthType.DXA },
      children: rows
    })]})]}
  );
}
function twoBox({ leftLabel, leftItems, leftBg, leftBd, rightLabel, rightItems, rightBg, rightBd }) {
  const half = Math.floor(W/2);
  function makeCell(label, items, bg, bc) {
    return new TableCell({
      borders:{ top:bd(bc,4), bottom:bd(bc,4), right:bd(bc,4),
                left:{ style:BorderStyle.SINGLE, size:14, color:bc } },
      shading:{ fill:bg, type:ShadingType.CLEAR },
      margins:{ top:120, bottom:120, left:180, right:180 },
      width:{ size:half, type:WidthType.DXA },
      children:[
        new Paragraph({ spacing:{after:60}, children:[new TextRun({ text:label, font:'Arial', size:17, bold:true, color:bc })] }),
        ...(items||[]).map(it => new Paragraph({
          spacing:{ line:320, lineRule:LineRuleType.AUTO, before:20, after:20 },
          children:[new TextRun({ text:'• '+String(it), font:'Arial', size:19, color:C.text })]
        }))
      ]
    });
  }
  return new Table({
    width:{ size:W, type:WidthType.DXA }, columnWidths:[half, W-half],
    rows:[new TableRow({ children:[
      makeCell(leftLabel, leftItems, leftBg, leftBd),
      makeCell(rightLabel, rightItems, rightBg, rightBd),
    ]})]
  });
}
function scoreBar(val, max=10) {
  const filled = Math.round((Number(val)||0)/max*10);
  return '█'.repeat(Math.min(filled,10)) + '░'.repeat(Math.max(0,10-filled)) + '  ' + String(val) + '/'+max;
}

// ── 데이터 ──
const inputPath  = process.argv[2] || '/home/claude/report_data.json';
const outputPath = process.argv[3] || '/home/claude/report_output.docx';
const raw  = JSON.parse(fs.readFileSync(inputPath,'utf8'));
const an   = raw.analysis  || {};
const wa   = raw.washing   || {};
const re   = raw.rewriting || {};
const mark      = an.mark?.final ?? 0;
const scores    = an.scores || {};
const verdict   = an.verdict || {};
const logline   = an.logline || {};
const pc        = an.pros_cons || {};
const drive     = an.drive || {};
const ev        = drive.evaluation || {};
const beats     = an.beats || {};
const genre     = an.genre_compliance || an.genre_suitability || {};
const washTable = wa.washing_table || [];
const da        = wa.dialogue_analysis || {};
const suggestions = wa.suggestions || [];
const rwData    = re.rewriting || {};
const scenes    = rwData.scenes || [];
const BEAT_KO = {
  'Opening Image':'오프닝 이미지','Theme Stated':'주제 제시','Set-up':'설정',
  'Catalyst':'촉매','Debate':'갈등','Break Into Two':'2막 진입',
  'B Story':'B 스토리','Fun and Games':'재미와 게임','Midpoint':'중간점',
  'Bad Guys Close In':'위기 고조','All Is Lost':'모든 것을 잃다',
  'Dark Night of Soul':'영혼의 어둔 밤','Dark Night of the Soul':'영혼의 어둔 밤',
  'Break Into Three':'3막 진입','Finale':'피날레','Final Image':'최종 이미지',
};
const circles = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨','⑩','⑪','⑫','⑬','⑭','⑮'];
const children = [];

// ━━ 표지 ━━
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ before:600, after:100 },
  children:[new TextRun({ text:'BLUE JEANS PICTURES', font:'Arial', size:18, color:C.gold, bold:true })] }));
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ before:0, after:60 },
  children:[new TextRun({ text:'시나리오 검토 보고서', font:'Arial', size:52, bold:true, color:C.navy })] }));
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ before:0, after:40 },
  children:[new TextRun({ text:an.title||'제목없음', font:'Arial', size:30, bold:true, color:C.text })] }));
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ before:60, after:80 },
  children:[new TextRun({ text:'REWRITE ENGINE  ·  Script Analysis Report', font:'Arial', size:17, color:C.sub })] }));
// PageBreak 제거 — 표지와 본문 연결

// ━━ 1. 종합 분석 — 4축 평가표 ━━
children.push(heading('1. 종합 분석  (Total Analysis) — Hollywood Standard'));
const verdictColor = verdict.status==='추천'?C.green : verdict.status==='비추천'?C.red : C.goldDark;
children.push(new Paragraph({ spacing:{ before:120, after:60 },
  children:[
    new TextRun({ text:String(mark), font:'Arial', size:80, bold:true, color:C.gold }),
    new TextRun({ text:'  / 10.0', font:'Arial', size:28, color:C.sub }),
    new TextRun({ text:'    '+String(verdict.status||''), font:'Arial', size:26, bold:true, color:verdictColor }),
  ]}));
children.push(colorBox({ label:'판정 근거', text:verdict.rationale, bg:C.bgBlue, borderColor:C.navy }));
children.push(gap(120));
children.push(heading('4축 정밀 평가  (Hollywood Standard)', 2));

const axW = [2400, 1400, 3400, W-2400-1400-3400];
const axHeader = new TableRow({ children:[
  ...['AXIS','가중치','평가 기준','점수'].map((t,i) =>
    new TableCell({ borders:bds(C.navy), shading:{fill:C.navy,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[i],type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:t,font:'Arial',size:17,bold:true,color:C.gold})]})] })
  )
]});
const axData = [
  { axis:'① STRUCTURE\n구성/플롯',  weight:'30%', criteria:'인과관계 정밀도\n3막 구조 완성도',       val:scores.structure||0, color:C.navy,    bg:C.light },
  { axis:'② HERO\n캐릭터',         weight:'30%', criteria:'Goal / Need / Strategy\n감정선의 선명도', val:scores.hero||0,      color:C.navy,    bg:C.white },
  { axis:'③ CONCEPT\n소재/컨셉',   weight:'20%', criteria:'하이컨셉 · 독창성\n시장성 있는 설정',     val:scores.concept||0,   color:C.goldDark,bg:C.light },
  { axis:'④ GENRE\n장르 적합성',   weight:'20%', criteria:'장르 문법 충실도\n타깃 관객 소구력',     val:scores.genre||0,     color:C.greenDk, bg:C.white },
];
const axRows = axData.map(d => new TableRow({ children:[
  new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
    margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[0],type:WidthType.DXA},
    children:[new Paragraph({spacing:{line:310, lineRule:LineRuleType.AUTO},children:[new TextRun({text:d.axis,font:'Arial',size:19,bold:true,color:C.navy})]})] }),
  new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
    margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[1],type:WidthType.DXA},
    children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:d.weight,font:'Arial',size:20,bold:true,color:C.navy})]})] }),
  new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
    margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[2],type:WidthType.DXA},
    children:[new Paragraph({spacing:{line:310, lineRule:LineRuleType.AUTO},children:[new TextRun({text:d.criteria,font:'Arial',size:18,color:C.text})]})] }),
  new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
    margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[3],type:WidthType.DXA},
    children:[new Paragraph({children:[new TextRun({text:scoreBar(d.val),font:'Courier New',size:17,color:d.color})]})] }),
]}));
const axFinal = new TableRow({ children:[
  new TableCell({ borders:bds(C.navy), shading:{fill:C.bgBlue,type:ShadingType.CLEAR},
    columnSpan:2, margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[0]+axW[1],type:WidthType.DXA},
    children:[new Paragraph({children:[new TextRun({text:'FINAL',font:'Arial',size:20,bold:true,color:C.navy})]})] }),
  new TableCell({ borders:bds(C.navy), shading:{fill:C.bgBlue,type:ShadingType.CLEAR},
    margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[2],type:WidthType.DXA},
    children:[new Paragraph({children:[new TextRun({text:'0.3S + 0.3H + 0.2C + 0.2G',font:'Arial',size:18,color:C.sub})]})] }),
  new TableCell({ borders:bds(C.navy), shading:{fill:C.bgBlue,type:ShadingType.CLEAR},
    margins:{top:80,bottom:80,left:120,right:120}, width:{size:axW[3],type:WidthType.DXA},
    children:[new Paragraph({children:[new TextRun({text:String(mark)+' / 10.0',font:'Arial',size:22,bold:true,color:C.gold})]})] }),
]});
children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:axW, rows:[axHeader,...axRows,axFinal] }));
children.push(divider());

// ━━ 2. 로그라인 ━━
children.push(heading('2. 로그라인 분석  (Logline Pack)'));
children.push(heading('ORIGINAL', 3));
children.push(colorBox({ text:logline.original, bg:'F5F5F5', borderColor:'AAAAAA', borderSize:8 }));
children.push(gap(80));
children.push(heading('✨ WASHED', 3));
children.push(colorBox({ text:logline.washed, bg:C.bgYellow, borderColor:C.gold }));
children.push(divider());

// ━━ 3. 줄거리 ━━
children.push(heading('3. 줄거리  (Synopsis)'));
children.push(colorBox({ text:an.synopsis, bg:C.bgBlue, borderColor:C.navy }));
children.push(divider());

// ━━ 4. 장단점 ━━
children.push(heading('4. 장점 및 보완점  (Pros & Cons)'));
children.push(twoBox({
  leftLabel:'✅  PROS',  leftItems:pc.pros||[],  leftBg:C.bgGreen, leftBd:C.green,
  rightLabel:'⚠️  CONS', rightItems:pc.cons||[], rightBg:C.bgRed,  rightBd:C.red,
}));
if (pc.prescription) {
  children.push(gap(120));
  children.push(colorBox({ label:'💊 핵심 처방 (Key Prescription)', text:pc.prescription, bg:C.bgYellow, borderColor:C.gold }));
}
children.push(divider());

// ━━ 5. 서사 동력 ━━
children.push(heading('5. 서사 동력  (Narrative Drive)'));
const dW3 = Math.floor(W/3);
children.push(new Table({
  width:{ size:W, type:WidthType.DXA }, columnWidths:[dW3, dW3, W-dW3*2],
  rows:[new TableRow({ children:
    [['① 목적(욕망)',drive.goal],['② 발생요인',drive.lack],['③ 해결전략',drive.strategy]].map(([lbl,val],i) =>
      new TableCell({
        borders:bds(C.gold), shading:{ fill:C.bgYellow, type:ShadingType.CLEAR },
        margins:{ top:100, bottom:100, left:140, right:140 },
        width:{ size:i===2?W-dW3*2:dW3, type:WidthType.DXA },
        children:[
          new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ after:60 },
            children:[new TextRun({ text:lbl, font:'Arial', size:17, bold:true, color:C.goldDark })] }),
          new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ line:300, lineRule:LineRuleType.AUTO },
            children:[new TextRun({ text:val||'-', font:'Arial', size:19, color:C.text })] }),
        ]
      })
    )
  })]
}));
children.push(gap(80));
children.push(colorBox({
  label:'서사 동력 평가',
  text:[`목적(욕망) 명확성: ${ev.clarity||'-'}`,`발생요인 확실성: ${ev.urgency||'-'}`,
        `해결전략 창의성: ${ev.consistency||'-'}`,'',ev.overall_diagnosis||''].join('\n'),
  bg:C.bgBlue, borderColor:C.navy
}));
children.push(divider());

// ━━ 6. 15-Beat Sheet ━━
children.push(heading('6. 구성 및 플롯  (15-Beat Sheet)'));
const beatKeys = Object.keys(beats).sort();
const beatRows2 = [
  new TableRow({ children:[
    new TableCell({ borders:bds(C.navy), shading:{fill:C.navy,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:2600,type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:'BEAT',font:'Arial',size:18,bold:true,color:C.gold})]})] }),
    new TableCell({ borders:bds(C.navy), shading:{fill:C.navy,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:W-2600,type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:'DESCRIPTION',font:'Arial',size:18,bold:true,color:C.gold})]})] }),
  ]}),
  ...beatKeys.map((k,idx) => {
    const name = k.replace(/^[\d\.\-\_\s]+/,'').trim();
    const ko   = BEAT_KO[name] || name;
    const bg   = idx%2===0 ? C.light : C.white;
    return new TableRow({ children:[
      new TableCell({ borders:bds('DDDDDD'), shading:{fill:bg,type:ShadingType.CLEAR},
        margins:{top:70,bottom:70,left:120,right:120}, width:{size:2600,type:WidthType.DXA},
        children:[
          new Paragraph({spacing:{after:20},children:[new TextRun({text:`${circles[idx]||''} ${ko}`,font:'Arial',size:19,bold:true,color:C.navy})]}),
          new Paragraph({children:[new TextRun({text:`(${name})`,font:'Arial',size:16,color:C.sub})]}),
        ] }),
      new TableCell({ borders:bds('DDDDDD'), shading:{fill:bg,type:ShadingType.CLEAR},
        margins:{top:70,bottom:70,left:120,right:120}, width:{size:W-2600,type:WidthType.DXA},
        children:[new Paragraph({spacing:{line:300, lineRule:LineRuleType.AUTO},children:[new TextRun({text:String(beats[k]||'-'),font:'Arial',size:19,color:C.text})]})] }),
    ]});
  })
];
children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:[2600,W-2600], rows:beatRows2 }));
children.push(divider());

// ━━ 7. 시각화 ━━
children.push(heading('7. 시각화  (Visualization)'));

// 긴장도 곡선 텍스트 표현
const tensionData = an.tension_data || [];
if (tensionData.length) {
  children.push(heading('긴장도 곡선  (Tension Arc)', 3));
  const maxT = Math.max(...tensionData.map(v=>Number(v)||0), 1);
  const tW = Math.floor(W / tensionData.length);
  const tRows = [
    new TableRow({ children: tensionData.map((v,i) =>
      new TableCell({
        borders: bds('EEEEEE'),
        shading: { fill: 'EEF0FA', type: ShadingType.CLEAR },
        margins: { top:60, bottom:60, left:40, right:40 },
        width: { size: tW, type: WidthType.DXA },
        children: [
          new Paragraph({ alignment: AlignmentType.CENTER, children:[
            new TextRun({ text: String(v||0), font:'Arial', size:18, bold:true, color:'191970' })
          ]}),
          new Paragraph({ alignment: AlignmentType.CENTER, children:[
            new TextRun({ text: '█'.repeat(Math.round((Number(v)||0)*4/10)), font:'Arial', size:10, color:'FFCB05' })
          ]}),
          new Paragraph({ alignment: AlignmentType.CENTER, children:[
            new TextRun({ text: `S${i+1}`, font:'Arial', size:14, color:'888888' })
          ]}),
        ]
      })
    )})
  ];
  children.push(new Table({ width:{size:W,type:WidthType.DXA}, rows:tRows }));
  children.push(gap(80));
}

// 인물 비중
const charNames  = (an.characters||{}).names  || [];
const charRatios = (an.characters||{}).ratios || [];
if (charNames.length && charRatios.length) {
  children.push(heading('인물 비중  (Narrative Share)', 3));
  const cW3 = [2200, W-4400, 2200];
  const charHdr = new TableRow({ children:
    ['인물','비중','점유율'].map((t,i) =>
      new TableCell({ borders:bds('191970'), shading:{fill:'191970',type:ShadingType.CLEAR},
        margins:{top:80,bottom:80,left:120,right:120}, width:{size:cW3[i],type:WidthType.DXA},
        children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:t,font:'Arial',size:17,bold:true,color:'FFCB05'})]})] })
    )
  });
  const charBodyRows = charNames.slice(0,6).map((name,i) => {
    const ratio = Number(charRatios[i])||0;
    return new TableRow({ children:[
      new TableCell({ borders:bds('DDDDDD'), shading:{fill:i%2===0?'F8F9FF':'FFFFFF',type:ShadingType.CLEAR},
        margins:{top:70,bottom:70,left:120,right:120}, width:{size:cW3[0],type:WidthType.DXA},
        children:[new Paragraph({children:[new TextRun({text:name,font:'Arial',size:19,bold:true,color:'191970'})]})] }),
      new TableCell({ borders:bds('DDDDDD'), shading:{fill:i%2===0?'F8F9FF':'FFFFFF',type:ShadingType.CLEAR},
        margins:{top:70,bottom:70,left:120,right:120}, width:{size:cW3[1],type:WidthType.DXA},
        children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:`${ratio}%`,font:'Arial',size:19,color:'191970'})]})] }),
      new TableCell({ borders:bds('DDDDDD'), shading:{fill:i%2===0?'F8F9FF':'FFFFFF',type:ShadingType.CLEAR},
        margins:{top:70,bottom:70,left:120,right:120}, width:{size:cW3[2],type:WidthType.DXA},
        children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({text:'█'.repeat(Math.round(ratio/10)),font:'Arial',size:14,color:'FFCB05'})]})] }),
    ]});
  });
  children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:cW3, rows:[charHdr,...charBodyRows] }));
}
children.push(divider());

// ━━ 8. 장르 ━━
children.push(heading('8. 장르 분석 및 적합도  (Genre Compliance)'));
children.push(kv('장르', genre.genre_key || genre.genre_name || '-'));
children.push(kv('준수도', `${genre.compliance_score||0} / 10   ${scoreBar(genre.compliance_score||0)}`));
// 장르적 재미 진단
if (genre.genre_fun_alive !== undefined) {
  children.push(kv('장르적 재미', genre.genre_fun_alive ? '✓ 작동' : '✗ 약함'));
}
if (genre.genre_fun_diagnosis) {
  children.push(gap(60));
  children.push(colorBox({ label:'🎬 장르적 재미 진단', text:genre.genre_fun_diagnosis, bg:C.bgYellow, borderColor:C.gold }));
}
children.push(gap(60));
// must_have_check (새 스키마)
const mustChecks = genre.must_have_check || [];
if (mustChecks.length) {
  children.push(heading('✅ 장르 필수 요소 체크', 3));
  mustChecks.forEach(c => {
    const icon = c.status === '충족' ? '✅' : (c.status === '약함' ? '△' : '❌');
    const cl   = c.status === '충족' ? C.greenDk : (c.status === '약함' ? C.goldDark : C.redDk);
    children.push(new Paragraph({
      spacing:{ line:340, lineRule:LineRuleType.AUTO, before:30, after:30 },
      children:[
        new TextRun({ text:`${icon} ${c.item||''} `, font:'Arial', size:19, bold:true, color:cl }),
        new TextRun({ text:`[${c.status||''}] `, font:'Arial', size:18, bold:true, color:cl }),
        new TextRun({ text:`— ${c.evidence||''}`, font:'Arial', size:18, color:C.text }),
      ]
    }));
  });
} else if ((genre.checks||[]).length) {
  // fallback: 이전 스키마
  children.push(heading('✅ 장르 문법 체크', 3));
  (genre.checks||[]).forEach(c => children.push(para('• '+c, {color:C.greenDk})));
}
// Hook/Punch 체크
const hp = genre.hook_punch_check || {};
if (hp.hook_note || hp.punch_note) {
  children.push(gap(60));
  children.push(heading('Hook / Punch 체크', 3));
  const hpHalf = Math.floor(W/2);
  children.push(new Table({
    width:{ size:W, type:WidthType.DXA }, columnWidths:[hpHalf, W-hpHalf],
    rows:[new TableRow({ children:[
      new TableCell({
        borders:{ top:bd(hp.hook_present?C.green:C.red,4), bottom:bd(hp.hook_present?C.green:C.red,4),
                  right:bd(hp.hook_present?C.green:C.red,4),
                  left:{ style:BorderStyle.SINGLE, size:12, color:hp.hook_present?C.green:C.red } },
        shading:{ fill:hp.hook_present?C.bgGreen:C.bgRed, type:ShadingType.CLEAR },
        margins:{top:100,bottom:100,left:160,right:160}, width:{size:hpHalf,type:WidthType.DXA},
        children:[
          new Paragraph({spacing:{after:40},children:[new TextRun({text:`${hp.hook_present?'✓':'✗'} Hook (오프닝)`,font:'Arial',size:17,bold:true,color:hp.hook_present?C.greenDk:C.redDk})]}),
          new Paragraph({spacing:{line:310, lineRule:LineRuleType.AUTO},children:[new TextRun({text:String(hp.hook_note||'-'),font:'Arial',size:18,color:C.text})]}),
        ]
      }),
      new TableCell({
        borders:{ top:bd(hp.punch_present?C.green:C.red,4), bottom:bd(hp.punch_present?C.green:C.red,4),
                  right:bd(hp.punch_present?C.green:C.red,4),
                  left:{ style:BorderStyle.SINGLE, size:12, color:hp.punch_present?C.green:C.red } },
        shading:{ fill:hp.punch_present?C.bgGreen:C.bgRed, type:ShadingType.CLEAR },
        margins:{top:100,bottom:100,left:160,right:160}, width:{size:W-hpHalf,type:WidthType.DXA},
        children:[
          new Paragraph({spacing:{after:40},children:[new TextRun({text:`${hp.punch_present?'✓':'✗'} Punch (결정타)`,font:'Arial',size:17,bold:true,color:hp.punch_present?C.greenDk:C.redDk})]}),
          new Paragraph({spacing:{line:310, lineRule:LineRuleType.AUTO},children:[new TextRun({text:String(hp.punch_note||'-'),font:'Arial',size:18,color:C.text})]}),
        ]
      }),
    ]})]
  }));
}
// 실패 패턴
const failPatterns = genre.fail_patterns_found || [];
if (failPatterns.length) {
  children.push(gap(60));
  children.push(heading('⚠️ 발견된 실패 패턴', 3));
  failPatterns.forEach(f => children.push(para('⚠ '+f, {color:C.redDk})));
}
if ((genre.missing_elements||[]).length) {
  children.push(gap(60));
  children.push(heading('❌ 누락된 필수 요소', 3));
  (genre.missing_elements||[]).forEach(m => children.push(para('• '+m, {color:C.redDk})));
}
children.push(gap(80));
if (genre.doctoring) {
  children.push(colorBox({ label:'장르 진단 (Doctoring)', text:genre.doctoring, bg:C.bgBlue, borderColor:C.navy }));
}
children.push(divider());

// ━━ 9. 시퀀스 워싱 ━━
children.push(new Paragraph({ children:[new PageBreak()] }));
children.push(heading('9. 시퀀스 워싱  (Washing Table)'));
const wHalf = Math.floor(W/2);
washTable.forEach(row => {
  children.push(new Paragraph({ spacing:{ before:160, after:60 },
    children:[
      new TextRun({ text:`${row.seq||''}  `, font:'Arial', size:22, bold:true, color:C.gold }),
      new TextRun({ text:row.label||'', font:'Arial', size:22, bold:true, color:C.navy }),
    ]}));
  children.push(new Table({
    width:{ size:W, type:WidthType.DXA }, columnWidths:[wHalf, W-wHalf],
    rows:[new TableRow({ children:[
      new TableCell({
        borders:{ top:bd('DDDDDD'), bottom:bd('DDDDDD'), right:bd('DDDDDD'),
                  left:{ style:BorderStyle.SINGLE, size:12, color:C.red } },
        shading:{ fill:'FFF5F5', type:ShadingType.CLEAR },
        margins:{ top:100, bottom:100, left:160, right:160 }, width:{ size:wHalf, type:WidthType.DXA },
        children:[
          new Paragraph({ spacing:{ after:60 }, children:[new TextRun({ text:'⚠️ 진단', font:'Arial', size:17, bold:true, color:C.redDk })] }),
          new Paragraph({ spacing:{ line:310, lineRule:LineRuleType.AUTO }, children:[new TextRun({ text:row.diagnosis||'-', font:'Arial', size:19, color:C.text })] })
        ]
      }),
      new TableCell({
        borders:{ top:bd('DDDDDD'), bottom:bd('DDDDDD'), right:bd('DDDDDD'),
                  left:{ style:BorderStyle.SINGLE, size:12, color:C.navy } },
        shading:{ fill:C.bgBlue, type:ShadingType.CLEAR },
        margins:{ top:100, bottom:100, left:160, right:160 }, width:{ size:W-wHalf, type:WidthType.DXA },
        children:[
          new Paragraph({ spacing:{ after:60 }, children:[new TextRun({ text:'✅ 처방', font:'Arial', size:17, bold:true, color:C.navy })] }),
          new Paragraph({ spacing:{ line:310, lineRule:LineRuleType.AUTO }, children:[new TextRun({ text:row.prescription||'-', font:'Arial', size:19, color:C.text })] })
        ]
      }),
    ]})]
  }));
});
children.push(divider());

// ━━ 10. 대사 워싱 (Dialogue Washing) ━━
children.push(heading('10. 대사 워싱  (Dialogue Washing)'));
children.push(new Paragraph({ spacing:{ before:60, after:80 },
  children:[new TextRun({ text:'① 캐릭터 적합성  ② 서브텍스트  ③ 행동/감정/관계 구동  ④ 개선 제안',
    font:'Arial', size:18, color:C.sub })] }));

if (da.axis_scores) {
  const ax = da.axis_scores;
  const dScore = da.overall_score||0;
  const dColor = dScore>=7?C.greenDk : dScore>=4?C.goldDark : C.redDk;
  const dW2 = [2800, 3600, W-2800-3600];
  const daHdr = new TableRow({ children:[
    ...['평가 축','기준','점수'].map((t,i) =>
      new TableCell({ borders:bds(C.navy), shading:{fill:C.navy,type:ShadingType.CLEAR},
        margins:{top:80,bottom:80,left:120,right:120}, width:{size:dW2[i],type:WidthType.DXA},
        children:[new Paragraph({children:[new TextRun({text:t,font:'Arial',size:17,bold:true,color:C.gold})]})] })
    )
  ]});
  const daAxes = [
    { label:'① 캐릭터 적합성', criteria:'고유 어휘·말투·감정 반영',   val:ax.character_voice||0, color:C.navy,    bg:C.light },
    { label:'② 서브텍스트',    criteria:'표면↔이면 충돌, 설명형 금지', val:ax.subtext||0,         color:'6B3FA0',  bg:C.white },
    { label:'③ 행동/감정/관계',criteria:'장면 추진력, 정보전달 금지',   val:ax.action_driven||0,   color:C.greenDk, bg:C.light },
  ];
  const daBodyRows = daAxes.map(d => new TableRow({ children:[
    new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:dW2[0],type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:d.label,font:'Arial',size:19,bold:true,color:C.navy})]})] }),
    new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:dW2[1],type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:d.criteria,font:'Arial',size:18,color:C.text})]})] }),
    new TableCell({ borders:bds('DDDDDD'), shading:{fill:d.bg,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:dW2[2],type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:scoreBar(d.val),font:'Courier New',size:17,color:d.color})]})] }),
  ]}));
  const daFinalRow = new TableRow({ children:[
    new TableCell({ borders:bds(C.navy), shading:{fill:C.bgBlue,type:ShadingType.CLEAR},
      columnSpan:2, margins:{top:80,bottom:80,left:120,right:120}, width:{size:dW2[0]+dW2[1],type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:'종합 대사 수준',font:'Arial',size:20,bold:true,color:C.navy})]})] }),
    new TableCell({ borders:bds(C.navy), shading:{fill:C.bgBlue,type:ShadingType.CLEAR},
      margins:{top:80,bottom:80,left:120,right:120}, width:{size:dW2[2],type:WidthType.DXA},
      children:[new Paragraph({children:[new TextRun({text:scoreBar(dScore),font:'Courier New',size:18,bold:true,color:dColor})]})] }),
  ]});
  children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:dW2, rows:[daHdr,...daBodyRows,daFinalRow] }));
  children.push(gap(100));
}

if (da.overall_comment) {
  children.push(colorBox({ label:'대사 총평', text:da.overall_comment, bg:C.bgBlue, borderColor:C.navy }));
  children.push(gap(80));
}
if ((da.strengths||[]).length) {
  children.push(heading('💪 대사 강점', 3));
  (da.strengths||[]).forEach(s => children.push(para('• '+s, {color:C.greenDk})));
  children.push(gap(80));
}

// 4축 Before/After 카드
if ((da.issues||[]).length) {
  children.push(heading('🔍 대사 4축 진단  Before / After', 2));
  const issH = Math.floor(W/2);
  (da.issues||[]).forEach(issue => {
    children.push(new Paragraph({ spacing:{ before:160, after:60 },
      children:[
        new TextRun({ text:`[${issue.type||''}]  `, font:'Arial', size:20, bold:true, color:C.red }),
        new TextRun({ text:String(issue.axis||''), font:'Arial', size:18, bold:true, color:C.navy }),
        new TextRun({ text:`  ${issue.description||''}`, font:'Arial', size:18, color:C.text }),
      ]}));
    children.push(new Table({
      width:{size:W,type:WidthType.DXA}, columnWidths:[issH, W-issH],
      rows:[new TableRow({ children:[
        new TableCell({
          borders:{ top:bd('DDDDDD'), bottom:bd('DDDDDD'), right:bd('DDDDDD'),
                    left:{ style:BorderStyle.SINGLE, size:12, color:C.red } },
          shading:{fill:'FFF5F5',type:ShadingType.CLEAR},
          margins:{top:100,bottom:100,left:160,right:160}, width:{size:issH,type:WidthType.DXA},
          children:[
            new Paragraph({spacing:{after:60},children:[new TextRun({text:'❌ BEFORE (원문)',font:'Arial',size:17,bold:true,color:C.redDk})]}),
            new Paragraph({spacing:{line:310, lineRule:LineRuleType.AUTO},children:[new TextRun({text:String(issue.example_bad||'-'),font:'Courier New',size:18,color:'333333'})]}),
          ]
        }),
        new TableCell({
          borders:{ top:bd('DDDDDD'), bottom:bd('DDDDDD'), right:bd('DDDDDD'),
                    left:{ style:BorderStyle.SINGLE, size:12, color:C.green } },
          shading:{fill:C.bgGreen,type:ShadingType.CLEAR},
          margins:{top:100,bottom:100,left:160,right:160}, width:{size:W-issH,type:WidthType.DXA},
          children:[
            new Paragraph({spacing:{after:60},children:[new TextRun({text:'✅ ④ 개선 제안 (AFTER)',font:'Arial',size:17,bold:true,color:C.greenDk})]}),
            new Paragraph({spacing:{line:310, lineRule:LineRuleType.AUTO},children:[new TextRun({text:String(issue.example_good||'-'),font:'Courier New',size:18,color:'333333'})]}),
          ]
        }),
      ]})]
    }));
    if (issue.rewrite_note) {
      children.push(colorBox({ label:'✏️  Moon 리라이팅 지시', text:String(issue.rewrite_note), bg:C.bgYellow, borderColor:C.gold }));
    }
    children.push(gap(60));
  });
}

// rewrite_directives: 내부 프롬프트용 - DOCX 미노출
children.push(divider());

// ━━ 11. 각색 제안 ━━
children.push(heading('11. 각색 제안  (Action Plan)'));
suggestions.forEach((s,i) => {
  const clean = String(s).replace(/^[\d\.\s]+/,'').trim();
  children.push(new Paragraph({
    spacing:{ line:340, lineRule:LineRuleType.AUTO, before:60, after:60 },
    children:[
      new TextRun({ text:`  STEP ${String(i+1).padStart(2,'0')}  `, font:'Arial', size:19, bold:true, color:C.white,
        shading:{ fill:C.navy, type:ShadingType.CLEAR } }),
      new TextRun({ text:'   '+clean, font:'Arial', size:19, color:C.text }),
    ]
  }));
});
children.push(divider());

// ━━ 12. 각색 원고 ━━
children.push(new Paragraph({ children:[new PageBreak()] }));
children.push(heading('12. 각색 원고  (Rewrite Scenes)'));
if (rwData.target_reason) {
  children.push(colorBox({ label:'✏️ 각색 전략', text:rwData.target_reason, bg:C.bgYellow, borderColor:C.gold }));
  children.push(gap(80));
}
const revised = scenes.filter(s=>s.type==='수정씬').length;
const added   = scenes.filter(s=>s.type==='추가씬').length;
children.push(new Paragraph({ spacing:{before:60,after:100},
  children:[
    new TextRun({ text:`총 ${scenes.length}개 씬  `, font:'Arial', size:20, bold:true, color:C.navy }),
    new TextRun({ text:`✏️ 수정씬 ${revised}개  `, font:'Arial', size:20, bold:true, color:C.green }),
    new TextRun({ text:`✨ 추가씬 ${added}개`, font:'Arial', size:20, bold:true, color:C.red }),
  ]}));
scenes.forEach(sc => {
  const isRevised = sc.type === '수정씬';
  const bc = isRevised ? C.green : C.red;
  const bg = isRevised ? C.bgGreen : C.bgRed;
  const icon = isRevised ? '✏️ 수정씬' : '✨ 추가씬';
  const insertBetween = sc.insert_between || '';
  children.push(new Paragraph({ spacing:{ before:240, after:60 },
    children:[
      new TextRun({ text:`${sc.scene_no||'Scene'}  `, font:'Arial', size:22, bold:true, color:C.navy }),
      new TextRun({ text:`[${icon}]`, font:'Arial', size:17, bold:true, color:bc }),
      ...(!isRevised && insertBetween ? [new TextRun({ text:`  ·  📍 ${insertBetween}`, font:'Arial', size:17, color:C.sub })] : []),
    ]}));
  if (!isRevised && insertBetween) {
    children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:[W],
      rows:[new TableRow({ children:[new TableCell({
        borders:{ top:bd(C.navy,4), bottom:bd(C.navy,4), right:bd(C.navy,4),
                  left:{ style:BorderStyle.SINGLE, size:10, color:C.navy } },
        shading:{fill:C.bgBlue,type:ShadingType.CLEAR},
        margins:{top:60,bottom:60,left:160,right:160}, width:{size:W,type:WidthType.DXA},
        children:[new Paragraph({children:[
          new TextRun({text:'📍 삽입 위치  ', font:'Arial', size:17, bold:true, color:C.navy}),
          new TextRun({text:insertBetween, font:'Arial', size:18, color:C.text}),
        ]})]
      })]})]}));
    children.push(gap(60));
  }
  if (sc.original) {
    children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:[W],
      rows:[new TableRow({ children:[new TableCell({
        borders:{ top:bd('CCCCCC',4), bottom:bd('CCCCCC',4), right:bd('CCCCCC',4),
                  left:{ style:BorderStyle.SINGLE, size:8, color:'AAAAAA' } },
        shading:{fill:'F5F5F5',type:ShadingType.CLEAR},
        margins:{top:80,bottom:80,left:160,right:160}, width:{size:W,type:WidthType.DXA},
        children:[
          new Paragraph({spacing:{after:40},children:[new TextRun({text:'📄 기존 씬 (BEFORE)',font:'Arial',size:16,bold:true,color:'888888'})]}),
          new Paragraph({spacing:{line:300, lineRule:LineRuleType.AUTO},children:[new TextRun({text:String(sc.original),font:'Arial',size:18,color:'555555'})]})
        ]
      })]})]}));
    children.push(gap(80));
  }
  const lines = String(sc.content||'').replace(/\\n/g,'\n').split('\n').filter(l=>l.trim());
  children.push(new Table({ width:{size:W,type:WidthType.DXA}, columnWidths:[W],
    rows:[new TableRow({ children:[new TableCell({
      borders:{ top:bd(bc,6), bottom:bd(bc,6), right:bd(bc,6), left:{ style:BorderStyle.SINGLE, size:16, color:bc } },
      shading:{fill:bg,type:ShadingType.CLEAR},
      margins:{top:120,bottom:120,left:200,right:200}, width:{size:W,type:WidthType.DXA},
      children:[
        new Paragraph({spacing:{after:60},children:[new TextRun({text:icon+' (AFTER)',font:'Arial',size:16,bold:true,color:bc})]}),
        ...lines.map(line => {
          const l = line.trim();
          if (l.startsWith('INT.')||l.startsWith('EXT.')) {
            return new Paragraph({spacing:{before:60,after:40},
              children:[new TextRun({text:l,font:'Courier New',size:20,bold:true,color:C.navy})]});
          } else if (l.includes(':') && l.split(':')[0]===l.split(':')[0].toUpperCase() && l.split(':')[0].length<25) {
            const [name,...rest] = l.split(':');
            return new Paragraph({spacing:{before:40,after:20},indent:{left:720},
              children:[
                new TextRun({text:name+': ',font:'Courier New',size:19,bold:true,color:C.navy}),
                new TextRun({text:rest.join(':').trim(),font:'Courier New',size:19,color:C.text})
              ]});
          } else {
            return new Paragraph({spacing:{line:300, lineRule:LineRuleType.AUTO,before:20,after:20},
              children:[new TextRun({text:l,font:'Courier New',size:18,color:'444444'})]});
          }
        })
      ]
    })]})]}));
  children.push(gap(80));
});

// ━━ 푸터 ━━
children.push(divider());
children.push(new Paragraph({ alignment:AlignmentType.CENTER, spacing:{ before:160 },
  children:[new TextRun({ text:'© 2026 BLUE JEANS PICTURES  ·  REWRITE ENGINE', font:'Arial', size:16, color:C.sub })] }));

// ━━ 문서 빌드 ━━
const doc = new Document({
  numbering:{ config:[{ reference:'bullets',
    levels:[{ level:0, format:LevelFormat.BULLET, text:'•', alignment:AlignmentType.LEFT,
      style:{ paragraph:{ indent:{ left:400, hanging:200 } } } }] }] },
  styles:{ default:{ document:{ run:{ font:'Arial', size:20, color:C.text } } } },
  sections:[{
    properties:{ page:{ size:{ width:11906, height:16838 }, margin:{ top:1134, right:1134, bottom:1134, left:1134 } }},
    headers:{ default: new Header({ children:[new Paragraph({
      alignment:AlignmentType.RIGHT,
      border:{ bottom:{ style:BorderStyle.SINGLE, size:4, color:C.gold } },
      spacing:{ after:100 },
      children:[
        new TextRun({ text:'BLUE JEANS PICTURES  ·  ', font:'Arial', size:16, color:C.gold, bold:true }),
        new TextRun({ text:an.title||'', font:'Arial', size:16, color:C.sub }),
      ]
    })]}) },
    children
  }]
});

Packer.toBuffer(doc)
  .then(buf => { fs.writeFileSync(outputPath, buf); console.log('OK'); })
  .catch(e => { console.error('ERR:',e.message); process.exit(1); });
