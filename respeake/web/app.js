const angleEl=document.querySelector('#angle'),beam=document.querySelector('#beam');
const voice=document.querySelector('#voice'),voiceDot=document.querySelector('#voiceDot');
const meter=document.querySelector('#meter'),levelText=document.querySelector('#levelText'),history=document.querySelector('#history');
const statusEl=document.querySelector('#status'),footer=document.querySelector('#footer');
async function refresh(){
  try{
    const data=await fetch('/api/state',{cache:'no-store'}).then(r=>r.json());
    const angle=Math.round(data.angle)%360,level=Math.round(data.level*100);
    const hardware=data.source==='respeaker';
    statusEl.innerHTML=`<i></i> ${hardware?'ReSpeaker 已连接':'模拟设备在线'}`;
    statusEl.classList.toggle('offline',!data.connected);
    footer.textContent=hardware?'实时硬件模式 · 雷达和灯环同步跟随声源':'演示模式 · 未读取真实硬件';
    angleEl.textContent=String(angle).padStart(3,'0')+'°';
    beam.style.transform=`rotate(${angle}deg)`;beam.style.opacity=data.voice?'.72':'.12';
    voice.textContent=data.voice?'检测到语音':'安静';voiceDot.classList.toggle('active',data.voice);
    meter.style.width=level+'%';levelText.textContent=level+'%';
    history.replaceChildren(...data.history.slice(-24).map(s=>{const i=document.createElement('i');i.style.height=(12+s.level*60)+'px';i.title=Math.round(s.angle)+'°';return i;}));
  }catch(e){statusEl.textContent='连接已断开'}
}
setInterval(refresh,140);refresh();

