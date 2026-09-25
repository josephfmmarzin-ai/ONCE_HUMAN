// =====================================================================
//  OPTIMISEUR — moteur de score dépendant de l'arme sélectionnée
// =====================================================================
const OPT = (function(){

  // ---------- Mécaniques (mots-clés) ----------
  const KW = {
    shrapnel:  {re:/shrapnel/i,                         fam:'weapon', fr:'Shrapnel',          en:'Shrapnel',        variant:'Shrapnel'},
    bounce:    {re:/bounce/i,                           fam:'weapon', fr:'Rebond',            en:'Bounce',          variant:'Bounce'},
    bullseye:  {re:/bull'?s eye|marked|mark /i,         fam:'weapon', fr:'Dans le mille',     en:"The Bull's Eye",  variant:"The Bull's Eye"},
    fastgunner:{re:/fast gunner/i,                      fam:'weapon', fr:'Tireur rapide',     en:'Fast Gunner',     variant:'Fast Gunner'},
    fortress:  {re:/fortress warfare/i,                 fam:'weapon', fr:'Lutte retranchée',  en:'Fortress Warfare',variant:'Fortress Warfare'},
    burn:      {re:/\bburn|blaze|burning/i,             fam:'status', fr:'Brûlure',           en:'Burn',            variant:'Burn'},
    surge:     {re:/power surge|\bshock/i,              fam:'status', fr:'Surtension',        en:'Power Surge',     variant:'Power Surge'},
    vortex:    {re:/frost vortex|frost construct|ice crystal|ice spike|\bfrost|frozen/i, fam:'status', fr:'Vortex de givre', en:'Frost Vortex', variant:'Frost Vortex'},
    bomber:    {re:/unstable bomber|\bbomb|explosion dmg|\bblast/i, fam:'status', fr:'Bombe instable', en:'Unstable Bomber', variant:'Unstable Bomber'},
  };
  const KW_ORDER = ['shrapnel','bounce','bullseye','fastgunner','fortress','burn','surge','vortex','bomber'];

  // Taux de coups au point faible selon le type d'arme (hypothèse de jeu propre)
  const WHR = {'Sniper Rifle':.85,'Crossbow':.8,'Pistol':.55,'Assault Rifle':.5,'SMG':.4,'LMG':.35,'Shotgun':.3,'Melee':.2,'Rocket Launcher':.1,'Flamethrower':.05};

  const STATS = ['wd','fr','cr','cd','ws','st','kw','hp','dr','rel','mel','mob'];
  const STAT_LABEL = {
    fr:{wd:"Dég d'arme / Attaque",fr:'Cadence',cr:'Taux crit',cd:'Dég crit',ws:'Point faible',st:'Statut / élémentaire / Psi',kw:'Dég de la mécanique',hp:'PV max',dr:'Réduction / bouclier / soin',rel:'Rechargement / chargeur',mel:'Mêlée',mob:'Mobilité / utilitaire'},
    en:{wd:'Weapon DMG / Attack',fr:'Fire rate',cr:'Crit rate',cd:'Crit DMG',ws:'Weakspot',st:'Status / elemental / Psi',kw:'Mechanic DMG',hp:'Max HP',dr:'Reduction / shield / heal',rel:'Reload / magazine',mel:'Melee',mob:'Mobility / utility'}
  };

  const GOALS = [
    ['dps',     {fr:'DPS global (le plus destructeur)', en:'Overall DPS (most destructive)'}],
    ['critdmg', {fr:'Dégâts critiques',               en:'Crit damage'}],
    ['critrate',{fr:'Taux de coup critique',          en:'Crit rate'}],
    ['weakspot',{fr:'Dégâts au point faible',         en:'Weakspot damage'}],
    ['elem',    {fr:'Élémentaire / statut',           en:'Elemental / status'}],
    ['keyword', {fr:"Dégâts de la mécanique de l'arme", en:"Weapon mechanic damage"}],
    ['survival',{fr:'Survie (PV / réduction)',        en:'Survival (HP / reduction)'}],
  ];

  // ---------- Style de PV (Normal / Semi-low life / Low life) ----------
  // hp = part de PV visée en combat. Seuils : semi-low life ≤ 50 %, low life < 30 % (zone Lunar).
  const HPMODES = {
    normal:{hp:.95, fr:'Normal (PV hauts)', en:'Normal (high HP)', dfr:"Tu restes au-dessus de 70–90 % de PV : bonus « PV élevés » actifs, effets Lunar faibles.", den:'You stay above 70–90% HP: “high HP” bonuses active, Lunar effects weak.'},
    semi:  {hp:.45, fr:'Semi-low life (≤ 50 % PV)', en:'Semi-low life (≤ 50% HP)', dfr:'Tu joues autour de 50 % de PV : effets « sous 50 % » actifs, suffixes Lunar déjà rentables.', den:'You play around 50% HP: “below 50%” effects active, Lunar suffixes already worth it.'},
    low:   {hp:.25, fr:'Low life / Lunar (< 30 % PV)', en:'Low life / Lunar (< 30% HP)', dfr:"Tu restes sous 30 % de PV : effets Lunar doublés, suffixes Lunar au maximum, bouclier et réduction de dégâts prioritaires. Le plus destructeur, mais fragile.", den:'You stay below 30% HP: Lunar effects doubled, Lunar suffixes maxed, shields and damage reduction first. The most destructive, but fragile.'},
  };
  const HP_ORDER = ['normal','semi','low'];
  // Lecture des conditions de PV d'un texte : gate = facteur d'activation, dbl = multiplicateur (« doubles if HP is below 30% »)
  function hpInfo(t, p){
    const hp = (HPMODES[p.mode]||HPMODES.normal).hp*100;
    let gate = 1, dbl = 1, hit = false, tt = t;
    // doublement / renforcement sous un seuil
    tt = tt.replace(/(?:;\s*)?(?:the )?(?:effect )?(?:doubles?|is doubled|becomes \+?\d+(?:\.\d+)?%)\s*(?:when|if|while)\s*(?:your )?hp\s*(?:is\s*)?(?:below|under|lower than|less than|<)\s*(\d+)%/gi,(m,x)=>{ hit=true; if(hp < +x) dbl = 2; return ' '; });
    tt = tt.replace(/effects? doubles? when hp is below (\d+)%/gi,(m,x)=>{ hit=true; if(hp < +x) dbl=2; return ' '; });
    // conditions sur les PV du joueur (pas ceux de l'ennemi)
    const enemy = /(enemy|enemies|target|targets)[^.]{0,25}hp/i;
    const below = tt.match(/(?:your )?hp (?:is )?(?:below|under|lower than|less than|<)\s*(\d+)%|below (\d+)% (?:of )?(?:max )?hp/i);
    if (below && !enemy.test(below.input.slice(Math.max(0,below.index-30), below.index+below[0].length))){ const x=+(below[1]||below[2]); hit=true; gate = hp < x ? 1 : (p.mode==='normal'? .1 : .2); }
    const above = tt.match(/(?:your )?hp (?:is )?(?:above|over|higher than|more than|>)\s*(\d+)%|above (\d+)% (?:of )?(?:max )?hp/i);
    if (above && !enemy.test(above.input.slice(Math.max(0,above.index-30), above.index+above[0].length))){ const x=+(above[1]||above[2]); hit=true; gate = hp > x ? 1 : .05; }
    if (/consum\w* (?:\+?\d+% )?(?:of )?(?:max )?hp|max hp consumed|lose \d+% (?:of )?(?:max )?hp/i.test(tt)){ hit=true; if (p.mode!=='normal') gate *= 1.3; }
    return {gate, dbl, hit, t: tt};
  }

  // ---------- Détection de la mécanique d'une arme ----------
  function detectKw(w){
    const txt = [w.effectName, w.effectEn, w.effect].filter(Boolean).join(' ');
    // ordre de priorité : le nom d'effet explicite d'abord
    if (w.effectName) for (const k of KW_ORDER) if (KW[k].re.test(w.effectName)) return k;
    for (const k of KW_ORDER) if (KW[k].re.test(txt)) return k;
    return null;
  }
  function num(x){ if(x==null||x==='') return null; const n=parseFloat(String(x).replace(',','.')); return isNaN(n)?null:n; }

  // Profil de l'arme : ce qui compte vraiment pour elle
  function profile(w, kwOverride, mode){
    const kw = kwOverride==='none' ? null : (kwOverride && kwOverride!=='auto' ? kwOverride : detectKw(w));
    const fam = kw ? KW[kw].fam : 'weapon';
    const whr = w.type==='Melee' ? .2 : (WHR[w.type] ?? .4);
    const cr0 = ((num(w.critRate) ?? 5) + 5)/100;          // crit de l'arme + base perso
    const cd0 = ((num(w.critDmg) ?? 25) + 50)/100;         // dég crit de l'arme + base perso
    const ws0 = ((num(w.weakspotDmg) ?? 40))/100;
    return {w, kw, fam, whr, cr0, cd0, ws0, melee: w.type==='Melee', detected: !kwOverride || kwOverride==='auto', mode: HPMODES[mode]?mode:'normal'};
  }

  // Poids par statistique = objectif × mécanique de l'arme × stats de base
  function weights(p, goal){
    const W = {}; STATS.forEach(s=>W[s]=0);
    // valeur marginale DPS de chaque stat pour CETTE arme (dérivée relative)
    // on raisonne avec un équipement « moyen » déjà en place (≈ +25 % crit, +35 % dég crit, +30 % point faible)
    const crE = Math.min(.9, p.cr0+.25), cdE = p.cd0+.35, wsE = p.ws0+.3;
    const crit = 1 + crE*cdE;
    const mCd = crE/crit, mCr = cdE/crit, mWs = p.whr/(1+p.whr*wsE);
    if (p.fam==='status'){
      // l'essentiel des dégâts vient de la mécanique (Intensité Psi) : balles secondaires
      Object.assign(W,{st:1.0, kw:1.25, wd:.18, fr:.15, cr:.05, cd:.05, ws:.05, rel:.12});
      if (p.kw==='bomber') { W.cr=.25; W.cd=.15; }             // Bombe instable peut critiquer
      if (p.kw==='surge')  { W.cr=.15; W.cd=.15; }             // certaines Surtension critiquent
    } else {
      Object.assign(W,{wd:1.0, fr:.9, cr:2.2*mCr, cd:2.2*mCd, ws:2.2*mWs, kw: p.kw?1.15:0, st:.05, rel:.25});
      if (p.kw==='shrapnel'){ W.cr*=1.2; W.cd*=1.2; W.ws*=1.2; } // Shrapnel crit & touche les points faibles
      if (p.kw==='bounce')  { W.ws*=1.15; }
      if (p.kw==='fortress'){ W.dr=.35; W.hp=.25; }
    }
    if (p.melee){ W.mel = 1.1; W.ws*=.5; W.fr=.1; }
    W.hp = Math.max(W.hp,.08); W.dr = Math.max(W.dr,.1); W.mob=.03;
    // style de PV : en low life les PV max servent peu, la réduction / le bouclier beaucoup
    if (p.mode==='low'){ W.hp*=.35; W.dr*=1.35; } else if (p.mode==='semi'){ W.hp*=.7; W.dr*=1.15; }
    const G = {
      dps:     s=>s,
      critdmg: s=>({...s, cd:s.cd*3+.8, cr:s.cr*1.6+.3, wd:s.wd*.4, fr:s.fr*.3, ws:s.ws*.3, st:s.st*.3, kw:s.kw*.5}),
      critrate:s=>({...s, cr:s.cr*3+.8, cd:s.cd*1.2+.2, wd:s.wd*.4, fr:s.fr*.3, ws:s.ws*.3, st:s.st*.3, kw:s.kw*.5}),
      weakspot:s=>({...s, ws:s.ws*3+.9, wd:s.wd*.5, fr:s.fr*.4, cr:s.cr*.5, cd:s.cd*.5, st:s.st*.3, kw:s.kw*.5}),
      elem:    s=>({...s, st:s.st*2.5+.9, kw:p.fam==='status'?s.kw*1.6:s.kw*.4, wd:s.wd*.25, fr:s.fr*.2, cr:s.cr*.3, cd:s.cd*.3, ws:s.ws*.3}),
      keyword: s=>({...s, kw:(s.kw||.5)*3, wd:s.wd*.6, st:s.st*.8}),
      survival:s=>({...s, hp:1.6, dr:1.8, rel:.3, mob:.15, wd:s.wd*.15, fr:s.fr*.1, cr:s.cr*.1, cd:s.cd*.1, ws:s.ws*.1, st:s.st*.15, kw:s.kw*.25, mel:(s.mel||0)*.2}),
    };
    return (G[goal]||G.dps)(W);
  }

  // ---------- Lecture d'un effet (texte anglais des fichiers du jeu) ----------
  const COND = /\b(when|after|while|if|for \d+(\.\d+)?s|every|upon|each time|triggering|below|above)\b/i;
  function kwOf(text){ const f=[]; for (const k of KW_ORDER) if (KW[k].re.test(text)) f.push(k); return f; }

  const HP_RX = /\bhp\b[^.;]{0,20}(?:below|under|lower|less|above|over|higher|more|<|>)|(?:below|above) \d+% (?:of )?(?:max )?hp|hp loss|hp lost|missing hp/i;
  // Découpe un texte en phrases ; une phrase sans chiffre (« doubles if HP… ») reste attachée à la précédente
  function clauses(text){
    const raw = text.split(/(?<=[.;])\s+/); const out=[];
    for (const c of raw){ const bare=c.replace(/hp[^.;%]{0,20}?\d+%|\d+% (?:of )?(?:max )?hp|cooldown:? ?\d+s/gi,''); if (out.length && !/\d+(?:\.\d+)?%|\+\d/.test(bare)) out[out.length-1]+=' '+c; else out.push(c); }
    return out;
  }
  function parse(text, p, _sub){
    const out = {}; const why = [];
    if (!text) return {out, why, off:false};
    // Effets à plusieurs phrases avec une condition de PV : chaque phrase a sa propre condition
    if (!_sub && HP_RX.test(text)){ const cs = clauses(text); if (cs.length>1){
      let off=false, hp=false, foreign=null; for (const c of cs){ const r=parse(c,p,true); if(r.off){ off=true; foreign=r.foreign; continue; } hp = hp||r.hp; for(const k in r.out) out[k]=(out[k]||0)+r.out[k]; why.push(...r.why); }
      if (off && !Object.keys(out).length) return {out:{}, why:[], off:true, foreign};
      return {out, why, off:false, hp};
    } }
    let t = ' '+text.replace(/\s+/g,' ')+' ';
    const H = hpInfo(t, p); t = H.t;
    const add = (s,v,label)=>{ if(!v) return; v*=H.dbl; out[s]=(out[s]||0)+v; why.push([s,v,label]); };
    // Mécaniques mentionnées
    const kws = kwOf(t).filter(k=>!(k==='bullseye' && /marked enemies dmg vs/i.test(t)));
    const own = p.kw && kws.includes(p.kw);
    const foreign = kws.filter(k=>k!==p.kw);
    // « marked » seul ne compte pas comme mécanique étrangère sans Bull's Eye explicite
    const strictForeign = foreign.filter(k=>!(k==='bullseye' && !/bull'?s eye/i.test(t)) && !(k==='vortex' && /frost resist/i.test(t)) && !(k==='burn' && /burn resist|heat/i.test(t)));
    if (strictForeign.length && !own) return {out:{}, why:[], off:true, foreign:strictForeign};
    let cond = COND.test(t) ? .7 : 1;
    // conditions contraignantes : accroupi immobile, non repéré, hors combat, PV bas…
    if (/crouch|immobile|not spotted|no enemies within|taking no dmg|out of combat|while airborne|in the air|while invisible/i.test(t)) cond = .4;
    else if (/stamina is (?:above|over)|enemy (?:with )?(?:hp )?above \d+% hp|enemy with hp above/i.test(t)) cond = Math.min(cond,.55);
    if (H.hit){ cond = Math.max(cond, .7) * H.gate; }
    if (/in a team|more than (?:1|one) (?:player|party member)|per (?:nearby )?ally|each nearby ally/i.test(t)) cond *= .5;   // joué en solo la plupart du temps
    if (/swimming|in water|dream zone|while vaulting|while rolling|while sprinting|when not in combat|in cold status|below 10°c|at 10°c/i.test(t)) cond *= .15;   // situations rares en combat
    if (/\bimpact\b/i.test(t) && !p.melee) cond *= .05;                                         // dégâts d'impact = coups de mêlée / charge
    if (/marked|mark(?:ed)? enem|the bull'?s eye/i.test(t) && p.kw!=='bullseye') cond *= .15;      // il faut une arme qui marque
    if (/shielded enemy|hitting a shield/i.test(t)) cond *= .4;
    if (p.melee && /bullet|magazine|reload|fire rate|weakspot/i.test(t) && !/melee/i.test(t)) cond *= .2;   // arme de mêlée
    if (/after (?:killing|defeating|getting \d+ kill)|upon (?:kill|defeat)|killing enem|precise kill|kill(?:s)? (?:an|\d)|when (?:defeating|a marked enemy is defeated)/i.test(t)) cond *= .6;
    // durée courte : « for 2s »
    const durM = t.match(/for (\d+(?:\.\d+)?)\s?s\b/i); if (durM){ const d=+durM[1]; if (d<=2) cond*=.35; else if (d<=4) cond*=.6; else if (d<=8) cond*=.85; }
    // « les N premiers coups » : proportion du chargeur
    const firstM = t.match(/first (\w+) hits?/i); if (firstM){ const n={one:1,two:2,three:3,four:4,five:5}[firstM[1].toLowerCase()]||+firstM[1]||3; cond*=Math.min(1,n/((p.w&&p.w.mag)||30)*1.5); }
    // plafonds « up to X% »
    const capM = t.match(/up to \+?(\d+(?:\.\d+)?)%/i);
    const stackM = t.match(/(?:up to|stack(?:s)? up to|stack(?:s)?) (\d+) (?:time|stack)/i) || t.match(/up to (\d+) stack/i);
    const stackN = stackM ? +stackM[1] : 0;
    const stackF = stackN ? Math.min(stackN,5)*.55 : 1;
    // valeurs « par stack » inversées : « grants 1% Elemental DMG … up to 20 stacks »
    t = t.replace(/(?:grants?|gain|gains)\s+(\d+(?:\.\d+)?)% (elemental|element|status|weapon|crit(?:ical)?|weakspot) (?:dmg|damage)/gi,(m,v,k)=>{
      const f = stackN ? Math.min(stackN,30)*.55 : 1; const val=+v*f*cond; const map={elemental:'st',element:'st',status:'st',weapon:'wd',crit:'cd',critical:'cd',weakspot:'ws'};
      add(map[k.toLowerCase()],val,'stacks'); return ' '; });

    // Bonus qui grandissent quand les PV baissent (« Every 10% HP loss grants +4% … DMG »)
    t = t.replace(/(?:every|for each|for every) (\d+)% (?:of )?(?:max )?hp (?:loss|lost|missing)[^.+]{0,25}?\+?(\d+(?:\.\d+)?)% ([a-z ,]{0,45}?)(?:dmg|damage)/gi,(m,step,v,list)=>{
      const miss = Math.max(0, 100 - (HPMODES[p.mode]||HPMODES.normal).hp*100); const n = Math.floor(miss/+step); const val=+v*n;
      if (/status|elemental/i.test(list)) add('st',val,'PV perdus'); if (/weapon|all|^\s*$/i.test(list)) add('wd',val,'PV perdus'); if (/melee/i.test(list)) add('mel',val,'PV perdus'); return ' '; });
    t = t.replace(/for every (\d+)% (?:decrease in|drop in|loss of) hp,?\s*([a-z ]{0,30}?)(dmg reduction|damage reduction|dmg|damage)\s*\+(\d+(?:\.\d+)?)%(?:,? up to \+?\d+(?:\.\d+)?%)?/gi,(m,step,list,kind,v)=>{
      const miss = Math.max(0, 100 - (HPMODES[p.mode]||HPMODES.normal).hp*100); const val=+v*Math.floor(miss/+step);
      if (/reduction/i.test(kind)) add('dr',val,'PV perdus'); else if (/status|elemental/i.test(list)) add('st',val,'PV perdus'); else add('wd',val,'PV perdus'); return ' '; });
    t = t.replace(/melee crit(?:ical)? (?:rate|dmg|damage)\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('mel',+v*.5*cond,'mêlée'); return ' '; });
    t = t.replace(/(\d+(?:\.\d+)?)% (?:weapon |status )?(?:dmg reduction|damage reduction)/gi,(m,v)=>{ add('dr',+v*cond*(stackN?Math.min(stackN,5)*.6:1),'réduction'); return ' '; });
    // Réductions de dégâts (avant les dégâts pour ne pas les confondre)
    t = t.replace(/((?:weapon |status |head |torso |weakspot |deviant |blast |explosion |melee )?dmg reduction|damage reduction|dmg taken -|dmg received -)\s*\+?(\d+(?:\.\d+)?)%?/gi,(m,a,v)=>{ add('dr',+v*cond,'réduction'); return ' '; });
    t = t.replace(/(dmg reduction|damage reduction) fluctuates[^.]*?(\d+)/gi,(m,a,v)=>{ add('dr',+v*.5,'réduction'); return ' '; });
    t = t.replace(/(\d+(?:\.\d+)?)% less (?:damage|dmg) to you/gi,(m,v)=>{ add('dr',+v*.15,'réduction'); return ' '; });
    // « pour chaque 1 % de taux crit, dégâts de la mécanique +0,5 % »
    t = t.replace(/for every 1% crit rate,?[^.+]{0,40}?\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add(own?'kw':'wd',+v*35,'selon le crit'); return ' '; });
    // Boucliers / soins
    t = t.replace(/shield (?:equal to|of) (\d+(?:\.\d+)?)% of (?:max )?hp/gi,(m,v)=>{ add('dr',+v*.6*cond,'bouclier'); return ' '; });
    t = t.replace(/(?:recover|restore|heal(?:s|ing)?)\s*(\d+(?:\.\d+)?)% (?:of )?(?:max )?hp/gi,(m,v)=>{ add('dr',+v*.5*cond,'soin'); return ' '; });
    if (/healing received|treatment in the backpack|lowest-grade treatment|revive/i.test(t)) add('dr',4*cond,'soin');
    // PV
    t = t.replace(/(?:max )?hp\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('hp',+v*cond,'PV %'); return ' '; });
    t = t.replace(/\bhp\s*\+\s*(\d{3,})/gi,(m,v)=>{ add('hp',+v/120,'PV'); return ' '; });
    // Listes « Melee, Weapon, and Status DMG +X% »
    t = t.replace(/((?:melee|weapon|status|elemental)(?:,? (?:and )?(?:melee|weapon|status|elemental))+) dmg\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,list,v)=>{
      const val=+v*cond*(capM&&+capM[1]>+v? Math.min(+capM[1]/+v,3)*.6:1);
      if(/weapon/i.test(list)) add('wd',val,'dég d\'arme'); if(/status|elemental/i.test(list)) add('st',val,'statut'); if(/melee/i.test(list)) add('mel',val,'mêlée'); return ' '; });
    // Crit
    t = t.replace(/crit(?:ical)? rate\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add(own && /(shrapnel|bounce|power surge|bomber)[^.]{0,20}crit rate/i.test(text)?'kw':'cr',+v*cond*stackF,'crit'); return ' '; });
    t = t.replace(/crit(?:ical)? (?:dmg|damage)\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('cd',+v*cond*stackF,'dég crit'); return ' '; });
    t = t.replace(/\+(\d+(?:\.\d+)?)% crit(?:ical)? (?:dmg|damage)/gi,(m,v)=>{ add('cd',+v*cond*stackF,'dég crit'); return ' '; });
    // Point faible
    t = t.replace(/weakspot (?:dmg|damage)\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('ws',+v*cond*stackF,'point faible'); return ' '; });
    if (/cannot deal weakspot/i.test(text)) add('ws',-60,'aucun point faible');
    // Élémentaire / statut / Psi
    t = t.replace(/(?:element(?:al)? dmg|status dmg|psi intensity(?: dmg)?|blaze dmg|frost dmg|shock dmg|blast dmg)(?: \([^)]*\))?\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('st',+v*cond*stackF,'statut'); return ' '; });
    t = t.replace(/(?:blaze|frost|shock|explosion|weapon) dmg received by (\d+(?:\.\d+)?)%/gi,(m,v)=>{ add(/weapon/i.test(m)?'wd':'st',+v*.8,'vulnérabilité'); return ' '; });
    // Mêlée (avant les dégâts génériques)
    t = t.replace(/melee (?:dmg|damage)\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('mel',+v*cond,'mêlée'); return ' '; });
    // Dégâts propres à une mécanique (Shrapnel DMG +60 %, Bounce DMG +125 %…)
    t = t.replace(/(shrapnel|bounce|power surge|unstable bomber|bomb's|bomb|frost vortex|frost construct\w*|burn)((?:'s)?[^.+]{0,30}?)(?:dmg|damage)([^.+]{0,12}?)\+\s*(\d+(?:\.\d+)?)%/gi,(m,a,b,c,v)=>{ if(own) add('kw',+v*cond*stackF,'mécanique'); return ' '; });
    // Dégâts d'arme / attaque
    t = t.replace(/(?:weapon dmg|weapon damage|attack|final dmg|bullet's final dmg|dmg dealt|dmg)\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{
      add('wd',+v*cond*stackF,'dég d\'arme'); return ' '; });
    t = t.replace(/vulnerability\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('wd',+v*cond,'vulnérabilité'); return ' '; });
    // Cadence, rechargement, chargeur
    t = t.replace(/fire rate\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('fr',+v*cond,'cadence'); return ' '; });
    t = t.replace(/(?:magazine capacity|reload efficiency|reload speed)\s*\+\s*(\d+(?:\.\d+)?)%/gi,(m,v)=>{ add('rel',+v*cond,'rechargement'); return ' '; });
    if (/refill|reload \d+|automatically reload|infinite ammo|consume reserve/i.test(t)) add('rel',8*cond,'munitions');
    // Mobilité / utilitaire
    if (/movement speed|sprint speed|stamina|max load|jump height|roll/i.test(t)) add('mob',8,'utilitaire');
    if (/gathering|logging|mining|max load \+\d/i.test(t)) add('mob',6,'récolte');
    // Effets de la mécanique sans chiffre (déclenchements, rebonds, stacks…)
    if (own){
      const counts = text.match(/(?:trigger count|bounces|trigger(?:s)? .{0,10}time|hit part|max .{0,20}stack(?:s)?|stacks)\s*\+\s*(\d+)/gi);
      if (counts) counts.forEach(c=>{ const n=+c.match(/(\d+)\s*$/)[1]; add('kw',n*12,'déclenchements'); });
      if (!out.kw && capM) add('kw',+capM[1]*.6*cond,'jusqu\'au plafond');
      if (!Object.keys(out).length){ const nums=[...text.matchAll(/(\d+(?:\.\d+)?)%/g)].map(x=>+x[1]).filter(x=>x<=300); add('kw',(nums.length?Math.max(...nums)*.25:8)*cond,'renforce la mécanique'); }
      else if (!out.kw) add('kw',3,'synergie mécanique');
    }
    return {out, why, off:false, hp:H.hit};
  }

  function scoreOf(parsed, W){ let s=0; for (const k in parsed.out) s += (W[k]||0)*parsed.out[k]; return s; }
  function explain(parsed, W){
    const L = STAT_LABEL[lang]||STAT_LABEL.fr;
    return parsed.why.filter(x=>W[x[0]]).map(([s,v])=>`${L[s]} ${v>0?'+':''}${Math.round(v*10)/10}`).slice(0,4).join(' · ');
  }
  const effEN = x => x.effectEn || x.effect || '';

  // Bonus de set dont l'effet n'a pas de chiffre direct (renforce le palier précédent)
  const SET_HINT = {'Shelterer|4':{st:6}, 'Lonewolf|4':{cd:9,cr:3}, 'Renegade|4':{rel:10,ws:3}, 'Agent|4':{rel:8,fr:4}, 'Bastille|4':{dr:8}, 'Savior|3':{dr:6}, 'Savior|4':{dr:10}, 'Stormweaver|4':{dr:6,hp:3}};
  // ---------- Recherche de l'armure (sets + pièce unique) ----------
  const SLOTS6 = ['Helmet','Mask','Top','Gloves','Bottoms','Shoes'];
  function armorSearch(p, W, allowKey){
    const sets = D.sets.filter(s=>s.name!=='Pièce unique' && s.bonus && s.bonus.length && s.mb!==false && s.pieces.some(id=>byId[id]&&!byId[id].legacy));
    const slotOf = {}; // set -> {slot: id}
    for (const s of sets){ slotOf[s.name]={}; for (const id of s.pieces){ const a=byId[id]; if(a && !a.legacy) slotOf[s.name][a.slot]=id; } }
    const cum = {}; // set -> [score(0..4), parsed per level]
    for (const s of sets){
      const arr=[0,0,0,0,0]; const why=[[],[],[],[],[]];
      for (let c=1;c<=4;c++){
        let sc=arr[c-1]; why[c]=why[c-1].slice();
        for (const b of s.bonus) if (b.pieces===c){ const pr=parse(b.effect,p); const h=SET_HINT[s.name+'|'+c]; if(h&&!pr.off) for(const k in h){ pr.out[k]=(pr.out[k]||0)+h[k]; pr.why.push([k,h[k],'set']); } const v=pr.off?0:scoreOf(pr,W); sc+=v; why[c].push({pieces:c,effect:b.effect,score:v,expl:explain(pr,W),off:pr.off}); }
        arr[c]=sc;
      }
      cum[s.name]={score:arr, why};
    }
    const keys = allowKey ? D.armor.filter(a=>a.set==='Pièce unique' && !a.legacy && effEN(a)) : [];
    const keyScored = keys.map(a=>{ const pr=parse(effEN(a),p); return {a, score: pr.off?-1:scoreOf(pr,W), expl:explain(pr,W), off:pr.off}; }).filter(k=>k.score>0);
    const patterns = {6:[[4,2],[4,1,1],[3,3],[3,2,1],[2,2,2]], 5:[[4,1],[3,2],[2,2,1],[3,1,1]]};
    const names = sets.map(s=>s.name);
    const results = [];
    const push = r => { if (results.length>=60 && r.score<=results[results.length-1].score) return; results.push(r); results.sort((a,b)=>b.score-a.score); if(results.length>60) results.length=60; };
    const feasible = (alloc, keySlot) => {  // alloc: [[set,count],...] → attribution des emplacements
      const free = SLOTS6.filter(s=>s!==keySlot); const assign = {};
      const rec = (i, left) => {
        if (i===alloc.length) return true;
        const [sn,c]=alloc[i]; const avail = free.filter(sl=>!assign[sl] && slotOf[sn][sl]);
        if (avail.length<c) return false;
        const choose=(start,k,picked)=>{ if(k===0){ picked.forEach(sl=>assign[sl]=sn); if(rec(i+1)) return true; picked.forEach(sl=>delete assign[sl]); return false; }
          for(let j=start;j<avail.length;j++){ if(choose(j+1,k-1,picked.concat(avail[j]))) return true; } return false; };
        return choose(0,c,[]);
      };
      return rec(0) ? assign : null;
    };
    const keyOpts = [null, ...keyScored];
    for (const k of keyOpts){
      const n = k ? 5 : 6; const base = k ? k.score : 0;
      for (const pat of patterns[n]){
        const iter = (i, used, alloc, sc) => {
          if (i===pat.length){ push({score:sc+base, alloc:alloc.slice(), key:k}); return; }
          for (const nm of names){
            if (used.includes(nm)) continue;
            if (i>0 && pat[i]===pat[i-1] && nm < alloc[i-1][0]) continue; // évite les doublons
            const v = cum[nm].score[Math.min(pat[i],4)];
            if (v<=0 && pat[i]>=2) continue;
            alloc.push([nm,pat[i]]); iter(i+1, used.concat(nm), alloc, sc+v); alloc.pop();
          }
        };
        iter(0,[],[],0);
      }
    }
    // vérification des emplacements (sets à 5 pièces) et dédoublonnage
    const out=[]; const seen=new Set();
    for (const r of results){
      const assign = feasible(r.alloc, r.key?r.key.a.slot:null); if (!assign) continue;
      const sig = r.alloc.map(x=>x[0]+x[1]).sort().join('|')+'|'+(r.key?r.key.a.id:'');
      if (seen.has(sig)) continue; seen.add(sig);
      const pieces = {}; for (const sl of SLOTS6){ if (r.key && r.key.a.slot===sl) pieces[sl]=r.key.a.id; else pieces[sl]=slotOf[assign[sl]][sl]; }
      out.push({...r, pieces, why: r.alloc.map(([nm,c])=>({set:nm, count:c, bonus:cum[nm].why[Math.min(c,4)]}))});
      if (out.length>=3) break;
    }
    return out;
  }

  // ---------- Mods + suffixes ----------
  const SUFFIX_VAL = {'Precision':{ws:7.2},'Violent':{cd:12},'Deviant Energy':{st:8},'Survival':{hp:4.8,dr:3.2},'General':{wd:2.4,rel:2},'Fury':{wd:5,cd:5},'Resistance':{dr:6},
    'Shrapnel':{kw:8},'Bounce':{kw:8},"The Bull's Eye":{kw:8},'Fast Gunner':{kw:8},'Fortress Warfare':{kw:8},'Burn':{kw:8},'Power Surge':{kw:8},'Frost Vortex':{kw:8},'Unstable Bomber':{kw:8},'Melee Default':{mel:8},
    'Mirror':{wd:4,cd:4,dr:3},'Mirror Deviant Energy':{st:6,dr:3},'Wild':{wd:4,cd:4,dr:3},'Wild Deviant Energy':{st:6,dr:3},'Battle':{wd:4,cd:4},
    'Downstar':{wd:3,cd:3},'Downstar Deviant Energy':{st:5},'Aero':{wd:2,cd:2},'Aero Deviant Energy':{st:3},'Resonance':{st:6},'Resonance Deviant Energy':{st:8}};
  // Suffixes qui dépendent des PV (valeurs légendaires estimées : Lunar ≈ Violent vers 75 % de PV, ~30 % de dég crit à PV bas)
  const SUFFIX_HP = {
    'Lunar':                  {normal:{cd:8,wd:2},  semi:{cd:18,wd:6}, low:{cd:30,wd:10}},
    'Lunar Deviant Energy':   {normal:{st:6},       semi:{st:13},      low:{st:22}},
    'Crescent':               {normal:{cd:6,wd:3},  semi:{cd:8,wd:4},  low:{cd:12,wd:5}},
    'Crescent Deviant Energy':{normal:{st:6},       semi:{st:8},       low:{st:11}},
    'Phantasmal':             {normal:{wd:3,cd:3},  semi:{wd:3,cd:3,dr:4}, low:{wd:3,cd:3,dr:8}},
    'Phantasmal Deviant Energy':{normal:{st:5},     semi:{st:5,dr:4},  low:{st:5,dr:8}},
  };
  const sufVal = (v,p) => SUFFIX_HP[v] ? SUFFIX_HP[v][p.mode||'normal'] : SUFFIX_VAL[v];
  function bestSuffix(variants, W, p){
    let best=null, bs=-1;
    for (const v of variants){ const val=sufVal(v,p); if(!val) continue;
      if (KW_ORDER.some(k=>KW[k].variant===v) && (!p.kw || KW[p.kw].variant!==v)) continue;
      let s=0; for (const k in val) s+=(W[k]||0)*val[k]; if (s>bs){bs=s;best=v;} }
    return best || variants[0];
  }
  function modsSearch(p, W){
    const res = {};
    const byName = {};
    for (const m of D.mods){ if (m.legacy) continue; const k=m.slot+'|'+m.name; (byName[k]=byName[k]||{slot:m.slot,name:m.name,effect:m.effect,items:[]}).items.push(m); }
    for (const sl of ['Weapon',...SLOTS6]){
      const cands = Object.values(byName).filter(x=>x.slot===sl || (x.slot==='All' && sl!=='Weapon')).map(x=>{ const pr=parse(x.effect,p); return {...x, score: pr.off?-1:scoreOf(pr,W), expl: explain(pr,W), off:pr.off}; })
        .filter(x=>x.score>0).sort((a,b)=>b.score-a.score);
      res[sl] = cands.slice(0,3).map(c=>{ const variants=[...new Set(c.items.map(i=>i.variant))]; const suf=bestSuffix(variants,W,p); const item=c.items.find(i=>i.variant===suf)||c.items[0]; return {...c, suffix:suf, id:item.id, variants}; });
    }
    return res;
  }

  // ---------- Peaux : effet selon la pièce d'armure + sets de peaux (4 pièces de la même famille) ----------
  function skinsSearch(p, W){
    const pool = D.skins.filter(x=>!x.legacy && x.slotEffects && Object.keys(x.slotEffects).length);
    const per = {};   // slot -> candidats triés
    for (const sl of SLOTS6){
      per[sl] = pool.filter(x=>x.slotEffects[sl]).map(x=>{ const pr=parse(x.slotEffects[sl],p); const sc=pr.off?0:scoreOf(pr,W); return {x, sl, e:x.slotEffects[sl], score:sc, expl:explain(pr,W), pr}; })
        .sort((a,b)=>b.score-a.score);
    }
    const free = {}; let freeScore=0; for (const sl of SLOTS6){ free[sl]=per[sl][0]; freeScore += free[sl]?free[sl].score:0; }
    let best = {slots:free, set:null, score:freeScore, setScore:0};
    for (const h of (D.hideSets||[])){
      const pr = parse(h.calc||h.effectEn, p); if (pr.off) continue; const hs = scoreOf(pr,W); if (hs<=0) continue;
      const fam = {}; for (const sl of SLOTS6){ fam[sl] = per[sl].find(c=>c.x.family===h.family); }
      const loss = SLOTS6.filter(sl=>fam[sl]).map(sl=>[sl, (free[sl]?free[sl].score:0) - fam[sl].score]).sort((a,b)=>a[1]-b[1]);
      if (loss.length < h.pieces) continue;
      const pickS = loss.slice(0,h.pieces); const slots = {...free}; let sc = freeScore + hs;
      for (const [sl,l] of pickS){ slots[sl]=fam[sl]; sc -= l; }
      if (sc > best.score) best = {slots, set:h, score:sc, setScore:hs, setExpl:explain(pr,W)};
    }
    return best;
  }

  // ---------- Déviation, Cradle, nourriture ----------
  const DEV_HINT = {'pyro-dino':{burn:30,st:10},'invincible-sun':{burn:15},'polar-jelly':{vortex:36},'snowsprite':{vortex:30},'chaos-snowsprite':{vortex:32},
    'mr-wish':{bullseye:30},'chaos-mr-wish':{bullseye:32},'mini-feaster':{bounce:30},'shattered-maiden':{bomber:40},'zapamander':{surge:25},
    'lonewolfs-whisper':{wd:21.6},'zapcam':{wd:21.6},'butterflys-emissary':{ws:30},'dr-teddy':{dr:30,hp:10},'festering-gel':{dr:28},'voodoo-doll':{dr:15},'enchanting-void':{mel:25}};
  function devSearch(p, W){
    return D.deviations.filter(d=>d.type==='Combat' && !d.legacy).map(d=>{
      const h = DEV_HINT[d.id]; let s=0, why=[];
      if (h){ for (const k in h){ if (KW[k]){ if(k===p.kw){ s+=W.kw*h[k]; why.push(STAT_LABEL[lang].kw+' +'+h[k]); } } else { s+=(W[k]||0)*h[k]; if(W[k]) why.push(STAT_LABEL[lang][k]+' +'+h[k]); } } }
      else { const pr=parse(effEN(d),p); if(!pr.off){ s=scoreOf(pr,W)*.6; why=[explain(pr,W)]; } }
      return {d, score:s, expl:why.filter(Boolean).join(' · ')};
    }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,3);
  }
  function cradleSearch(p, W){
    const cur = D.cradle.some(c=>c.current) ? D.cradle.filter(c=>c.current) : D.cradle;
    return cur.map(c=>{ const pr=parse(c.effect,p); return {c, score: pr.off?-1:scoreOf(pr,W)*(c.style==='Scenario'?.85:1), expl:explain(pr,W)}; })
      .filter(x=>x.score>0).sort((a,b)=>b.score-a.score).filter((x,i,arr)=>arr.findIndex(y=>y.c.name===x.c.name)===i).slice(0,8);
  }
  const MEAT = {shrapnel:['Viande d\'ours pure','Pure Bear Meat'],bounce:['Volaille pure','Pure Poultry'],bullseye:['Viande de cerf','Venison'],fastgunner:['Viande de lièvre','Hare Meat'],
    fortress:['Viande de tortue fine','Fine Turtle Meat'],burn:['Viande de chèvre pure','Pure Goat Meat'],surge:['Viande de crocodile pure','Pure Crocodile Meat'],vortex:['Bœuf pur','Pure Beef'],bomber:['Porc pur','Pure Pork']};
  function foodHints(p, W, goal){
    const L = lang==='en';
    const out = [];
    if (p.kw) out.push({n: L?`Mixed Fried Hot Dog + ${MEAT[p.kw][1]} + milk`:`Hot-dog frit mixte + ${MEAT[p.kw][0]} + lait`, e: L?`${KW[p.kw].en} DMG +3% (pure meat), slight Max HP (milk). Cook it on the Protoplasm Fusion Stove (+40% effect, +75% duration).`:`DÉG de ${KW[p.kw].fr} +3 % (viande pure), PV max légèrement ↑ (lait). À cuire au Réchaud de fusion de protoplasme (+40 % d'effet, +75 % de durée).`});
    if (goal==='survival') out.push({n: L?'Taco (bear meat) / Malt Ale':'Taco (viande d\'ours) / Bière au malt', e: L?'+100 Max HP (bear meat); Malt Ale: sanity + pollution immunity 30 min.':'+100 PV max (viande d\'ours) ; Bière au malt : santé mentale + immunité pollution 30 min.'});
    else if (p.kw==='shrapnel') out.push({n: L?'Canned Meat':'Viande en boîte (Canned Meat)', e: L?'Shrapnel DMG +10%.':'DÉG de Shrapnel +10 %.'});
    else if (p.fam==='status' || goal==='elem') out.push({n: L?'Whimsical Drink':'Boisson fantasque (Whimsical Drink)', e: L?'Status DMG +25%.':'DÉG de statut +25 %.'});
    else if (goal==='weakspot' || W.ws>=W.cd && W.ws>=W.cr) out.push({n: L?'Assorted Canned Fruit':'Mélange de fruits en conserve', e: L?'Weakspot DMG +25% while sanity > 80%.':'DÉG aux points faibles +25 % si santé mentale > 80 %.'});
    else out.push({n: L?'Stargazy Pie':'Tourte Stargazy (Stargazy Pie)', e: L?'Crit DMG +25% while Energy is full.':'DÉG critiques +25 % si l\'énergie est pleine.'});
    out.push({n: L?'Bone-in Deviated Sausage (bosses)':'Saucisse déviante cuite à l\'os (boss)', e: L?'DMG vs bosses +15%.':'DÉG contre les boss +15 %.'});
    return out.slice(0,3);
  }
  function foodSearch(p, W){
    return D.food.filter(f=>f.rarity!=='common' && f.category!=='Materials' && /dmg|crit|weakspot|attack|psi|hp|reduction|fire rate|reload/i.test(f.effect||'')).map(f=>{ const pr=parse(f.effect,p); return {f, score: pr.off?-1:scoreOf(pr,W), expl:explain(pr,W)}; })
      .filter(x=>x.score>0).sort((a,b)=>b.score-a.score).filter((x,i,arr)=>arr.findIndex(y=>y.f.name===x.f.name)===i).slice(0,2);
  }

  // ---------- Estimation de DPS / indice ----------
  function totals(res, p){
    const T={}; STATS.forEach(s=>T[s]=0);
    const addParsed=(txt)=>{ const pr=parse(txt,p); if(!pr.off) for(const k in pr.out) T[k]+=pr.out[k]; };
    const a=res.armor[0]; if(a){ a.why.forEach(w=>w.bonus.forEach(b=>{ if(!b.off) addParsed(b.effect); })); if(a.key) addParsed(effEN(a.key.a)); }
    for (const sl in res.mods){ const m=res.mods[sl][0]; if(m){ addParsed(m.effect); const sv=sufVal(m.suffix,p)||{}; for(const k in sv) T[k]+=sv[k]; } }
    for (const sl in res.skins.slots){ const s=res.skins.slots[sl]; if(s) addParsed(s.e); }
    if (res.skins.set) addParsed(res.skins.set.calc||res.skins.set.effectEn);
    return T;
  }
  function estimate(p, T){
    const w=p.w; const base = (w.damage && w.rpm) ? w.damage*w.rpm/60 : null;
    const mult = (x)=> (1+(x.wd||0)/100)*(1+(x.fr||0)/100)*(1+Math.min(1,p.cr0+(x.cr||0)/100)*(p.cd0+(x.cd||0)/100))*(1+p.whr*(p.ws0+(x.ws||0)/100));
    const m0 = mult({}), m1 = mult(T);
    const statusIdx = (1+(T.st||0)/100)*(1+(T.kw||0)/100);
    return {base, dps0: base? Math.round(base*m0):null, dps1: base? Math.round(base*m1):null, gain: Math.round((m1/m0-1)*100), statusGain: Math.round((statusIdx-1)*100)};
  }

  function run(weaponId, goal, kwOverride, allowKey, mode){
    const w = byId[weaponId]; if(!w) return null;
    const p = profile(w, kwOverride, mode); const W = weights(p, goal);
    const res = {p, W, goal, mode:p.mode, armor: armorSearch(p,W,allowKey), mods: modsSearch(p,W), skins: skinsSearch(p,W), dev: devSearch(p,W), cradle: cradleSearch(p,W), food: foodSearch(p,W)};
    res.foodHints = foodHints(p,W,goal); res.totals = totals(res,p); res.est = estimate(p,res.totals);
    return res;
  }
  return {run, KW, KW_ORDER, GOALS, STAT_LABEL, STATS, detectKw, profile, SLOTS6, HPMODES, HP_ORDER};
})();

// ---------------- Interface de l'onglet Optimiseur ----------------
const OT = {
  fr:{tab:'Optimiseur',weapon:'Arme',goal:'Objectif',mech:"Mécanique de l'arme",auto:'Détection automatique',none:'Aucune (dégâts d\'arme purs)',allowKey:'Autoriser une pièce unique (Key Armor)',hpMode:'Style de PV',hpIntro:'Les builds LUNAR (PV bas) sont en général les plus destructeurs : les suffixes Lunar et les peaux Lunar montent en puissance quand tes PV baissent.',mode:'Style',hideSet:'Set de peaux',noHideSet:'Aucun set de peaux rentable ici : peaux choisies pièce par pièce.',lunarNote:'Valeurs des suffixes Lunar / Crescent / Phantasmal estimées (non publiées par le jeu).',
      run:'Optimiser',intro:"Choisis une arme et un objectif, puis « Optimiser ». Le moteur lit la mécanique de l'arme (Shrapnel, Brûlure, Rebond…), ses stats de base (crit, point faible, type) et calcule la meilleure combinaison de sets, mods + suffixes, peaux, déviation, overrides et nourriture pour CETTE arme.",
      profile:"Profil de l'arme",detected:'Mécanique détectée',notDetected:"Non détectée dans la base — choisis-la dans « Mécanique de l'arme » si tu la connais",family:'Type de dégâts',famW:"Dégâts d'arme (crit, point faible, attaque)",famS:'Dégâts de statut (Intensité Psi, élémentaire)',whr:'Coups au point faible estimés',weights:'Ce qui compte pour cette arme (poids)',
      armor:'Armure optimale',alt:'Alternatives',set:'Set',pieces:'pièces',key:'Pièce unique',mods:'Mods et suffixes',slot:'Emplacement',mod:'Mod',suffix:'Suffixe',why:'Pourquoi',skins:'Peaux',dev:'Déviation',cradle:'Cradle (8 overrides)',food:'Nourriture',
      est:'Estimation',dps0:'DPS théorique sans équipement',dps1:'DPS théorique avec ce build',gain:'Gain indicatif (dégâts d\'arme)',sgain:'Indice indicatif (statut / mécanique)',load:'Charger dans « Mon build »',loaded:'Build chargé dans Mon build',
      score:'score',note:"Moteur de score : il additionne les effets lus dans les fichiers du jeu, pondérés selon l'arme et l'objectif. Il donne la bonne direction et un ordre de grandeur, pas le calcul exact du jeu (formules non publiques). Les effets conditionnels sont comptés à ~70 %. Peaux : effet selon la pièce (meta-builds) + sets de peaux ×4 (relevé communautaire). Style de PV : les effets « PV au-dessus / en dessous de X % » et « double sous 30 % » sont activés ou coupés selon le style choisi. Cradle : la liste de ta saison (ex. Shunter) peut différer, garde les effets équivalents.",
      offKw:'ignoré : autre mécanique',noEffect:"Cette arme n'a pas d'effet spécial renseigné : le moteur optimise en « dégâts d'arme purs ».",
      slots:{Weapon:'Arme',Helmet:'Casque',Mask:'Masque',Top:'Haut',Gloves:'Gants',Bottoms:'Bas',Shoes:'Chaussures'},
      suf:{'Precision':'Précision','Violent':'Violent','Deviant Energy':'Énergie déviante','Survival':'Survie','General':'Général','Lunar':'Lunaire','Lunar Deviant Energy':'Lunaire Énergie déviante','Crescent':'Croissant','Crescent Deviant Energy':'Croissant Énergie déviante','Phantasmal':'Fantasmal','Phantasmal Deviant Energy':'Fantasmal Énergie déviante','Mirror':'Miroir','Wild':'Sauvage','Downstar':'Plongeant','Aero':'Aérien','Battle':'Combat','Resonance':'Résonance'}},
  en:{tab:'Optimizer',weapon:'Weapon',goal:'Goal',mech:'Weapon mechanic',auto:'Auto-detect',none:'None (pure weapon damage)',allowKey:'Allow one Key Armor piece',hpMode:'HP style',hpIntro:'LUNAR (low HP) builds are usually the most destructive: Lunar suffixes and Lunar hides get stronger as your HP drops.',mode:'Style',hideSet:'Hide set',noHideSet:'No worthwhile hide set here: hides picked piece by piece.',lunarNote:'Lunar / Crescent / Phantasmal suffix values are estimates (not published by the game).',
      run:'Optimize',intro:"Pick a weapon and a goal, then « Optimize ». The engine reads the weapon's mechanic (Shrapnel, Burn, Bounce…), its base stats (crit, weakspot, type) and computes the best combination of sets, mods + suffixes, skins, deviation, overrides and food for THIS weapon.",
      profile:'Weapon profile',detected:'Detected mechanic',notDetected:"Not found in the database — pick it in « Weapon mechanic » if you know it",family:'Damage type',famW:'Weapon damage (crit, weakspot, attack)',famS:'Status damage (Psi Intensity, elemental)',whr:'Estimated weakspot hits',weights:'What matters for this weapon (weights)',
      armor:'Optimal armor',alt:'Alternatives',set:'Set',pieces:'pieces',key:'Key Armor',mods:'Mods and suffixes',slot:'Slot',mod:'Mod',suffix:'Suffix',why:'Why',skins:'Skins',dev:'Deviation',cradle:'Cradle (8 overrides)',food:'Food',
      est:'Estimate',dps0:'Theoretical DPS without gear',dps1:'Theoretical DPS with this build',gain:'Indicative gain (weapon damage)',sgain:'Indicative index (status / mechanic)',load:'Load into « My build »',loaded:'Build loaded into My build',
      score:'score',note:'Scoring engine: it sums the effects read from the game files, weighted by weapon and goal. It gives the right direction and order of magnitude, not the exact in-game calculation (formulas are not public). Conditional effects count ~70%. Hides: effect by armor piece (meta-builds) + ×4 hide sets (community findings). HP style: “HP above / below X%” and “doubles below 30%” effects are switched on or off according to the chosen style. Cradle: your season list (e.g. Shunter) may differ; keep equivalent effects.',
      offKw:'ignored: other mechanic',noEffect:'This weapon has no special effect in the database: the engine optimizes for pure weapon damage.',
      slots:{Weapon:'Weapon',Helmet:'Helmet',Mask:'Mask',Top:'Top',Gloves:'Gloves',Bottoms:'Bottoms',Shoes:'Shoes'},
      suf:{}}
};
const ot = k => OT[lang][k] ?? OT.fr[k];
let OPTS = {w: restore('opt_w','socr-the-last-valor'), goal: restore('opt_goal','dps'), kw: 'auto', key: true, hp: restore('opt_hp','normal'), res: null};

function optRun(){
  store('opt_w',OPTS.w); store('opt_goal',OPTS.goal); store('opt_hp',OPTS.hp);
  OPTS.res = OPT.run(OPTS.w, OPTS.goal, OPTS.kw, OPTS.key, OPTS.hp); render();
}
function optLoad(){
  const r=OPTS.res; if(!r) return; const a=r.armor[0]; const b={name:`Optimiseur — ${r.p.w.name} — ${OPT.GOALS.find(g=>g[0]===r.goal)[1][lang]} — ${OPT.HPMODES[r.mode][lang].split(' (')[0]}`};
  b.w1=r.p.w.id; if(r.mods.Weapon[0]) b.wm1=r.mods.Weapon[0].id;
  if(a) for(const sl of OPT.SLOTS6){ b[sl]=a.pieces[sl]; const m=r.mods[sl]&&r.mods[sl][0]; if(m) b['m_'+sl]=m.id; }
  for(const sl of OPT.SLOTS6){ const s=r.skins.slots[sl]; if(s) b['sk_'+sl]=s.x.id; }
  if(r.dev[0]) b.dev=r.dev[0].d.id; if(r.cradle[0]) b.ovr=r.cradle[0].c.id;
  state.build=b; store('current',b); toast(ot('loaded')); state.tab='build'; render();
}
function sufL(v){ return (OT[lang].suf||{})[v] || v; }
function renderOptimFilters(){
  const ws = D.weapons.slice().sort((a,b)=>(a.type+a.name).localeCompare(b.type+b.name));
  const types=[...new Set(ws.map(w=>w.type))];
  const rk={legendary:0,epic:1,rare:2,uncommon:3,common:4};
  const opt = types.map(ty=>`<optgroup label="${esc(sub(ty))}">${ws.filter(w=>w.type===ty).sort((a,b)=>(rk[a.rarity]-rk[b.rarity])||a.name.localeCompare(b.name)).map(w=>`<option value="${w.id}" ${OPTS.w===w.id?'selected':''}>${esc(w.name)}${w.rarity==='legendary'?' ★':''}${OPT.detectKw(w)?' · '+OPT.KW[OPT.detectKw(w)][lang]:''}</option>`).join('')}</optgroup>`).join('');
  return `<aside class="filters">
    <h3>${ot('weapon')}</h3><select class="sort" onchange="OPTS.w=this.value;OPTS.kw='auto';OPTS.res=null;render()">${opt}</select>
    <h3>${ot('goal')}</h3><div class="chips">${OPT.GOALS.map(([g,l])=>`<button class="chip ${OPTS.goal===g?'on':''}" onclick="OPTS.goal='${g}';OPTS.res=null;render()">${l[lang]}</button>`).join('')}</div>
    <h3>${ot('mech')}</h3><select class="sort" onchange="OPTS.kw=this.value;OPTS.res=null;render()">
      <option value="auto" ${OPTS.kw==='auto'?'selected':''}>${ot('auto')}</option><option value="none" ${OPTS.kw==='none'?'selected':''}>${ot('none')}</option>
      ${OPT.KW_ORDER.map(k=>`<option value="${k}" ${OPTS.kw===k?'selected':''}>${OPT.KW[k][lang]}</option>`).join('')}</select>
    <h3>${ot('hpMode')}</h3><div class="hpmode">${OPT.HP_ORDER.map(m=>{const H=OPT.HPMODES[m]; return `<label class="${OPTS.hp===m?'on':''}"><input type="checkbox" ${OPTS.hp===m?'checked':''} onchange="OPTS.hp='${m}';OPTS.res=null;render()"><span><b>${H[lang]}</b><small>${lang==='fr'?H.dfr:H.den}</small></span></label>`}).join('')}</div>
    <p style="font-size:11.5px;color:var(--star);margin-top:6px">${ot('hpIntro')}</p>
    <label style="display:flex;gap:6px;margin-top:10px;font-size:13px;color:var(--ink2)"><input type="checkbox" ${OPTS.key?'checked':''} onchange="OPTS.key=this.checked;OPTS.res=null;render()">${ot('allowKey')}</label>
    <button class="btn primary" style="width:100%;margin-top:14px;font-size:16px;padding:10px" onclick="optRun()">⚙ ${ot('run')}</button>
    <p style="font-size:12px;color:var(--ink3);margin-top:12px">${ot('intro')}</p></aside>`;
}
function bar(v,max){ return `<div class="gauge"><i style="width:${Math.max(3,Math.min(100,v/max*100))}%"></i></div>`; }
function renderOptim(){
  const w=byId[OPTS.w]; const p=OPT.profile(w,OPTS.kw,OPTS.hp);
  const prof = (()=>{ const W=(OPTS.res&&OPTS.res.W)||null; const kwName = p.kw? OPT.KW[p.kw][lang] : '—';
    return `<div class="summary"><h3>${ot('profile')} — ${esc(w.name)}</h3>
      <div style="display:grid;grid-template-columns:72px 1fr;gap:12px;align-items:start">${img(w,'thumb')}
      <table><tr><td>${ot('detected')}</td><td><b style="color:var(--teal)">${esc(kwName)}</b>${!p.kw&&OPTS.kw==='auto'?`<div class="todo" style="font-size:12px">${ot('notDetected')}</div>`:''}</td></tr>
      <tr><td>${ot('family')}</td><td>${p.fam==='status'?ot('famS'):ot('famW')}</td></tr>
      <tr><td>${ot('mode')}</td><td><b style="color:${p.mode==='low'?'var(--red)':p.mode==='semi'?'var(--star)':'var(--ink)'}">${OPT.HPMODES[p.mode][lang]}</b></td></tr>
      <tr><td>${ot('whr')}</td><td>${Math.round(p.whr*100)} % · crit ${Math.round(p.cr0*100)} % · ${lang==='fr'?'dég crit':'crit DMG'} ${Math.round(p.cd0*100)} %</td></tr></table></div>
      ${W?`<h3 class="mt">${ot('weights')}</h3><table>${OPT.STATS.filter(s=>W[s]>.12).sort((a,b)=>W[b]-W[a]).map(s=>`<tr><td>${OPT.STAT_LABEL[lang][s]}</td><td>${bar(W[s],Math.max(...OPT.STATS.map(x=>W[x])))}</td></tr>`).join('')}</table>`:''}</div>`; })();
  const r = OPTS.res;
  if(!r) return `<section class="build"><h2>${ot('tab')}</h2><div style="grid-column:1/3">${prof}</div><p style="grid-column:1/3;color:var(--ink2)">${ot('intro')}</p></section>`;
  const a = r.armor[0];
  const armorHtml = a? `<table><tr><td>${ot('slot')}</td><td></td></tr>${OPT.SLOTS6.map(sl=>{const x=byId[a.pieces[sl]]; return `<tr><td>${ot('slots')[sl]}</td><td style="display:flex;gap:8px;align-items:center">${img(x,'thumb')}<div><b>${esc(x.name)}</b><div class="sm" style="color:var(--ink2);font-size:12px">${x.set==='Pièce unique'?ot('key'):esc(x.set)} · ${x.hp||'?'} ${t('hp')}</div></div></td></tr>`}).join('')}</table>
    ${a.why.map(s=>`<p class="eff"><b>${esc(s.set)} ×${s.count}</b> — ${s.bonus.map(b=>`${b.pieces}p : ${esc(b.effect)}${b.off?` <span class="todo">(${ot('offKw')})</span>`:''}${b.expl?` <span style="color:var(--star)">[${esc(b.expl)}]</span>`:''}`).join(' · ')||'—'}</p>`).join('')}
    ${a.key?`<p class="eff"><b>${ot('key')} : ${esc(a.key.a.name)}</b> — ${esc(eff(a.key.a))} <span style="color:var(--star)">[${esc(a.key.expl)}]</span></p>`:''}`:'<p class="todo">—</p>';
  const alts = r.armor.slice(1).map(x=>`<li>${x.alloc.map(([n,c])=>`${esc(n)} ×${c}`).join(' + ')}${x.key?` + ${esc(x.key.a.name)}`:''} <span class="todo">(${ot('score')} ${Math.round(x.score)} / ${Math.round(a.score)})</span></li>`).join('');
  const modsHtml = `<table><tr><td>${ot('slot')}</td><td>${ot('mod')} &lt;${ot('suffix')}&gt; — ${ot('why')}</td></tr>${['Weapon',...OPT.SLOTS6].map(sl=>{const m=r.mods[sl][0]; if(!m) return `<tr><td>${ot('slots')[sl]}</td><td>—</td></tr>`; const alt=r.mods[sl].slice(1).map(z=>esc(z.name)).join(', ');
      return `<tr><td>${ot('slots')[sl]}</td><td><b>${esc(m.name)}</b> <span style="color:var(--teal)">&lt;${esc(sufL(m.suffix))}&gt;</span><div style="font-size:12px;color:var(--ink2)">${esc(m.effect)}</div><div style="font-size:11.5px;color:var(--star)">${esc(m.expl)}</div>${alt?`<div class="todo" style="font-size:11px">${ot('alt')} : ${alt}</div>`:''}</td></tr>`}).join('')}</table>`;
  const hs = r.skins.set;
  const skinsHtml = `${hs?`<p class="eff"><b style="color:var(--teal)">${ot('hideSet')} : ${esc(hsName(hs))} ×${hs.pieces}</b> — ${esc(hsEff(hs))}${r.skins.setExpl?` <span style="color:var(--star)">[${esc(r.skins.setExpl)}]</span>`:''}</p>`:`<p class="todo" style="font-size:12px">${ot('noHideSet')}</p>`}
    <table>${OPT.SLOTS6.map(sl=>{const s=r.skins.slots[sl]; if(!s) return `<tr><td>${ot('slots')[sl]}</td><td>—</td></tr>`; return `<tr><td>${ot('slots')[sl]}</td><td style="display:flex;gap:8px;align-items:center">${img(s.x,'thumb')}<div><b>${esc(s.x.name)}</b>${hs&&s.x.family===hs.family?' <span class="badge new">set</span>':''}<div style="font-size:12px;color:var(--ink2)">${esc(s.e)}</div>${s.expl?`<div style="font-size:11.5px;color:var(--star)">${esc(s.expl)}</div>`:''}</div></td></tr>`}).join('')}</table>`;
  const devHtml = r.dev.map((x,i)=>`<p class="eff">${i===0?'<b>':''}${esc(x.d.name)}${i===0?'</b>':''} — <span style="color:var(--star)">${esc(x.expl)}</span></p>`).join('')||'<p class="todo">—</p>';
  const crHtml = r.cradle.map(x=>`<p class="eff"><b>${esc(x.c.name)}</b> — ${esc(x.c.effect)}</p>`).join('');
  const foodHtml = (r.foodHints||[]).map(x=>`<p class="eff"><b>${esc(x.n)}</b> — ${esc(x.e)}</p>`).join('')||'<p class="todo">—</p>';
  const e=r.est;
  const estHtml = `<div class="big3">${statBox(ot('dps0'),e.dps0??'—')}${statBox(ot('dps1'),e.dps1??'—')}${statBox(r.p.fam==='status'?ot('sgain'):ot('gain'), (r.p.fam==='status'?e.statusGain:e.gain)+' %')}</div>`;
  return `<section class="build">
    <h2>${ot('tab')} — ${esc(w.name)} · ${OPT.GOALS.find(g=>g[0]===r.goal)[1][lang]} · ${OPT.HPMODES[r.mode][lang]}</h2>
    <div class="buildbar"><button class="btn primary" onclick="optLoad()">${ot('load')}</button><span class="saved">${!p.kw?ot('noEffect'):''}</span></div>
    <div style="display:flex;flex-direction:column;gap:14px">${prof}
      <div class="summary"><h3>${ot('est')}</h3>${estHtml}</div>
      <div class="summary"><h3>${ot('armor')}</h3>${armorHtml}${alts?`<h3 class="mt">${ot('alt')}</h3><ul style="font-size:12.5px">${alts}</ul>`:''}</div></div>
    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="summary"><h3>${ot('mods')}</h3>${modsHtml}</div>
      <div class="summary"><h3>${ot('skins')}</h3>${skinsHtml}</div>
      <div class="summary"><h3>${ot('dev')}</h3>${devHtml}<h3 class="mt">${ot('cradle')}</h3>${crHtml}<h3 class="mt">${ot('food')}</h3>${foodHtml}</div></div>
    <p style="grid-column:1/3;font-size:11.5px;color:var(--ink3)">${ot('note')} ${ot('lunarNote')}</p>
  </section>`;
}
