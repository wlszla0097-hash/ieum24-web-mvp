const state={programs:[],source:'sample'};
const byId=(id)=>document.getElementById(id);
const clean=(value)=>String(value??'').trim();

function setSource(source,note=''){
  const badge=byId('source-status');
  const label=badge?.querySelector('span:last-child');
  if(!badge||!label)return;
  badge.classList.toggle('is-sample',source==='sample');
  badge.classList.toggle('is-error',source==='error');
  label.textContent=source==='work24'?'고용24 공개 정보 연동':source==='error'?'정보 연결 확인 필요':'시연용 예시 정보';
  byId('source-caption').textContent=note|| (source==='work24'?'정보 출처: 고용24 OpenAPI · 최신 모집·자격은 공식 공고에서 확인해 주세요.':'현재는 시연용 예시 정보를 보여드려요. 고용24 OpenAPI 연결 뒤 실제 공개 정보로 바뀝니다.');
}

function element(tag,className,text){const node=document.createElement(tag);if(className)node.className=className;if(text!==undefined)node.textContent=text;return node;}

function renderPrograms(){
  const list=byId('program-list');if(!list)return;
  const interest=clean(byId('interest')?.value||'all');
  const region=clean(byId('region')?.value||'');
  const query=clean(byId('recent-program')?.value||'').toLocaleLowerCase('ko-KR');
  const filtered=state.programs.filter((p)=>{
    const topic=interest==='all'||p.category.includes(interest)||p.tags.some((t)=>t.includes(interest));
    const location=!region||!p.region||p.region.includes(region)||p.region.includes('전국');
    const previous=!query||`${p.title} ${p.summary} ${p.category} ${p.tags.join(' ')}`.toLocaleLowerCase('ko-KR').includes(query)||state.programs.length<5;
    return topic&&location&&previous;
  });
  list.replaceChildren();list.setAttribute('aria-busy','false');
  byId('results-count').textContent=filtered.length?`살펴볼 수 있는 정보 ${filtered.length}건`:'조건에 맞는 정보가 없어요';
  if(!filtered.length){list.append(element('div','empty-state','관심 분야를 전체로 바꾸거나 다른 지역을 선택해 보세요.'));return;}
  const icons={취업:'↗',훈련:'✳',기업:'＋'};
  for(const p of filtered){
    const card=element('article','program-card');
    card.append(element('span','program-icon',icons[p.category]||'◎'));
    const copy=element('div','program-copy');
    copy.append(element('p','program-category',p.category||'고용지원'),element('h3','',p.title),element('p','program-summary',p.summary));
    const meta=element('div','program-meta');
    if(p.region)meta.append(element('span','program-tag',p.region));
    if(p.end_date)meta.append(element('span','program-tag',`마감 ${p.end_date}`));
    if(p.is_sample)meta.append(element('span','program-tag example','예시 정보'));
    copy.append(meta);
    const link=element('a','program-link','공식 정보 확인 ↗');link.href=p.source_url;link.target='_blank';link.rel='noreferrer';link.setAttribute('aria-label',`${p.title} 공식 정보 확인, 새 창`);
    card.append(copy,link);list.append(card);
  }
}

async function loadPrograms(){
  const list=byId('program-list');
  try{
    const response=await fetch('/api/programs',{headers:{Accept:'application/json'},signal:AbortSignal.timeout(12000)});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||'공개 정보를 불러오지 못했어요.');
    state.programs=Array.isArray(data.programs)?data.programs:[];
    state.source=data.source||'sample';setSource(state.source,data.note?`${data.note} ${state.source==='sample'?'현재 목록은 시연용 예시 정보입니다.':''}`:'');renderPrograms();
  }catch(error){
    state.programs=[];state.source='error';setSource('error','공개 정보를 불러오지 못했어요. 잠시 뒤 새로고침해 주세요.');
    list?.replaceChildren(element('div','error-state','정보 연결에 문제가 생겼어요. 잠시 뒤 다시 시도해 주세요.'));list?.setAttribute('aria-busy','false');byId('results-count').textContent='정보를 불러오지 못했어요';
  }
}

byId('program-filter')?.addEventListener('submit',(event)=>{event.preventDefault();renderPrograms();});
byId('interest')?.addEventListener('change',renderPrograms);
byId('region')?.addEventListener('change',renderPrograms);

const question=byId('question');
question?.addEventListener('input',()=>{byId('char-count').textContent=`${question.value.length} / 500`;});

function renderAI(data){
  const area=byId('ai-result');area.replaceChildren();area.hidden=false;
  const title=element('h3','',data.items?.length?'이런 정보를 살펴볼 수 있어요':'다른 표현으로 한 번 더 물어봐 주세요.');area.append(title);
  for(const item of (data.items||[]).slice(0,3)){
    const card=element('article','ai-result-card');card.append(element('strong','',item.title));
    if(item.reason)card.append(element('p','',item.reason));
    if(item.next_step)card.append(element('p','',`확인할 내용 · ${item.next_step}`));
    if(item.source_name){const source=element('a','ai-result-source',`${item.source_name}에서 확인 ↗`);source.href=item.source_url||'https://www.work24.go.kr/';source.target='_blank';source.rel='noreferrer';card.append(source);}
    area.append(card);
  }
}

byId('recommend-form')?.addEventListener('submit',async(event)=>{
  event.preventDefault();
  const message=byId('ai-message'),result=byId('ai-result'),button=byId('recommend-button');
  const text=clean(question.value);
  result.hidden=true;result.replaceChildren();message.className='form-message';
  if(!text){message.textContent='질문을 한 줄 적어 주세요.';message.classList.add('is-error');question.focus();return;}
  if(text.length>500){message.textContent='질문은 500자 이내로 작성해 주세요.';message.classList.add('is-error');return;}
  button.disabled=true;button.textContent='정보를 살펴보고 있어요…';message.textContent='공개된 사업 정보를 바탕으로 안내를 정리하고 있어요.';
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),22000);
  try{
    const response=await fetch('/api/recommend',{method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},body:JSON.stringify({question:text,interest:byId('interest')?.value,region:byId('region')?.value,recent_program:byId('recent-program')?.value}),signal:controller.signal});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||'안내를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.');
    renderAI(data);message.textContent=data.message||'참고 결과예요. 신청 전 공식 공고를 확인해 주세요.';message.classList.add('is-success');
  }catch(error){message.textContent=error.name==='AbortError'?'응답이 늦어 안내를 마치지 못했어요. 잠시 후 다시 시도해 주세요.':error.message;message.classList.add('is-error');}
  finally{clearTimeout(timeout);button.disabled=false;button.innerHTML='AI 안내 받기 <span aria-hidden="true">↗</span>';}
});

const menu=byId('primary-nav'),toggle=document.querySelector('.menu-toggle');
toggle?.addEventListener('click',()=>{const open=menu.classList.toggle('is-open');toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'메뉴 닫기':'메뉴 열기');});
menu?.querySelectorAll('a').forEach((link)=>link.addEventListener('click',()=>{menu.classList.remove('is-open');toggle?.setAttribute('aria-expanded','false');}));

loadPrograms();
