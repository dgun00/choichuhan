<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 권역 소개 글래스 배너 -->
    <!-- 🌊 영웅(Hero) 배너 영역 (레이아웃 및 타이포그래피 개선) -->
    <div class="relative z-10 flex flex-col md:flex-row justify-between items-center gap-8 mb-8 bg-gradient-to-br from-white/70 to-white/30 p-8 sm:p-12 rounded-[2.5rem] border border-white/80 shadow-[0_8px_30px_rgb(14,165,233,0.08)] backdrop-blur-xl overflow-hidden">
    <!-- 배경 장식 -->
    <div class="absolute -right-10 -top-20 w-72 h-72 bg-sky-300/20 rounded-full blur-3xl pointer-events-none"></div>
    
    <!-- 왼쪽 텍스트 영역 -->
    <div class="relative z-10 max-w-2xl">
      <div class="flex flex-wrap items-center gap-2 mb-6">
        <span class="bg-sky-50 text-sky-700 text-[11px] font-extrabold px-3 py-1.5 rounded-full border border-sky-100 shadow-sm flex items-center tracking-wide">
          <span class="w-1.5 h-1.5 rounded-full bg-sky-500 animate-pulse mr-1.5"></span>실시간 익명 커뮤니티
        </span>
        <span class="bg-indigo-50 text-indigo-600 text-[11px] font-extrabold px-3 py-1.5 rounded-full border border-indigo-100 shadow-sm tracking-wide">
          ✨ 공공데이터 100% 연동
        </span>
      </div>
      
      <!-- 줄간격(leading)과 폰트 웨이트 조절로 세련미 강조 -->
      <h2 class="text-3xl sm:text-5xl font-black leading-[1.25] mb-5 text-slate-800 tracking-tight" style="word-break: keep-all; letter-spacing: -0.03em;">
        부산의 모든 순간을 잇다,<br/>
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 via-blue-500 to-indigo-600 block mt-2 pb-1">
          우리의 파도타기 🌊
        </span>
      </h2>
      
      <p class="text-slate-600 text-[15px] sm:text-base font-medium leading-relaxed max-w-lg bg-white/40 p-4 rounded-2xl border border-white/60 shadow-sm">
        숨겨진 해변 명소부터 현지인만 아는 찐맛집까지.<br/>
        로그인 없이 자유롭게 나누고, AI 갈매기에게 부산을 물어보세요!
      </p>
    </div>

    <!-- 오른쪽 3D/글래스모피즘 아트웍 (빈 공간 채우기) -->
    <div class="relative z-10 hidden md:flex w-56 h-56 shrink-0 items-center justify-center">
      <div class="relative w-full h-full flex items-center justify-center animate-float">
        <!-- 배경 컬러 쉐도우 -->
        <div class="absolute inset-0 bg-gradient-to-tr from-sky-300 to-indigo-400 rounded-[2.5rem] rotate-12 opacity-70 blur-md"></div>
        <!-- 메인 유리 패널 -->
        <div class="absolute inset-0 bg-white/50 backdrop-blur-xl border-2 border-white rounded-[2.5rem] -rotate-6 shadow-2xl flex items-center justify-center text-7xl transition-transform hover:rotate-0 duration-300 cursor-default">
          🌉
        </div>
        <!-- 장식용 미니 뱃지 -->
        <div class="absolute -bottom-3 -right-3 bg-white backdrop-blur-md border border-sky-100 rounded-full w-16 h-16 flex items-center justify-center shadow-xl text-3xl animate-bounce" style="animation-duration: 3s;">
          🐬
        </div>
        <div class="absolute -top-4 -left-4 bg-sky-500 rounded-full w-10 h-10 flex items-center justify-center shadow-lg text-lg border-2 border-white z-20 text-white">
          ⭐
        </div>
      </div>
    </div>
  </div>

    <!-- 📈 통계 차트 그리드 -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="bg-white/50 backdrop-blur-lg border border-white/70 shadow-lg shadow-slate-200/50 p-6 rounded-[2rem]">
        <h3 class="text-[15px] font-bold text-slate-800 flex items-center mb-4"><span class="mr-2 text-xl drop-shadow-sm">🎯</span> 카테고리별 현황</h3>
        <div class="h-60 flex justify-center items-center">
          <canvas ref="categoryChartRef"></canvas>
        </div>
      </div>
      <div class="bg-white/50 backdrop-blur-lg border border-white/70 shadow-lg shadow-slate-200/50 p-6 rounded-[2rem]">
        <h3 class="text-[15px] font-bold text-slate-800 flex items-center mb-4"><span class="mr-2 text-xl drop-shadow-sm">📍</span> 핫플레이스 분포</h3>
        <div class="h-60 flex justify-center items-center">
          <canvas ref="regionChartRef"></canvas>
        </div>
      </div>
      <div class="bg-white/50 backdrop-blur-lg border border-white/70 shadow-lg shadow-slate-200/50 p-6 rounded-[2rem]">
        <h3 class="text-[15px] font-bold text-slate-800 flex items-center mb-4"><span class="mr-2 text-xl drop-shadow-sm">🏆</span> 주간 인기 권역</h3>
        <div ref="regionStatsRef" class="h-60 w-full flex items-center justify-center"></div>
      </div>
    </div>


    <!-- 📅 축제 캘린더 영역 -->
    <div class="bg-white/50 backdrop-blur-lg border border-white/70 shadow-lg shadow-slate-200/50 p-6 sm:p-8 rounded-[2rem] relative mt-6">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-2">
        <h3 class="text-lg font-bold text-slate-800 flex items-center">
          <span class="mr-2 text-2xl drop-shadow-sm">🎇</span> 부산 축제·행사 캘린더
        </h3>
        <span class="text-xs text-sky-700 bg-sky-50/80 font-bold px-3 py-1.5 rounded-full border border-sky-200">
          일정을 클릭하면 상세 정보를 볼 수 있어요!
        </span>
      </div>
      <div ref="festivalCalendarRef" class="bg-white/60 backdrop-blur-md rounded-2xl p-4 border border-white min-h-[450px]"></div>
      
      <!-- 툴팁 (마우스 오버시 정보) -->
      <div v-if="hoveredEvent" class="absolute z-50 w-72 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-blue-100 p-4 text-xs space-y-2 pointer-events-none animate-fade-in transition-all"
          :style="{ left: hoveredEvent.x + 'px', top: hoveredEvent.y + 'px' }">
        <img v-if="hoveredEvent.image" :src="hoveredEvent.image" class="w-full h-32 object-cover rounded-xl mb-2 shadow-sm border border-slate-100">
        <p class="font-bold text-base text-slate-800 leading-snug">{{ hoveredEvent.title }}</p>
        <div class="space-y-1.5 text-slate-600 bg-slate-50/80 p-2.5 rounded-xl border border-slate-100/50">
          <p class="flex"><span class="w-4 mr-1">📍</span> <span class="flex-1 line-clamp-1 font-medium">{{ hoveredEvent.place || '장소 미정' }}</span></p>
          <p class="flex"><span class="w-4 mr-1">🕐</span> <span class="flex-1">{{ hoveredEvent.playtime || '시간 안내 없음' }}</span></p>
          <p class="flex"><span class="w-4 mr-1">💳</span> <span class="flex-1">{{ hoveredEvent.fee || '무료 또는 안내 없음' }}</span></p>
        </div>
      </div>
    </div>

    <!-- [모달 1]: 축제·행사 상세 정보 모달 -->
    <div v-if="selectedFestival" @click.self="closeFestivalDetail" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div @click.stop class="bg-white/95 backdrop-blur-2xl w-full max-w-2xl rounded-[2rem] p-6 sm:p-8 shadow-2xl border border-white space-y-5 max-h-[85vh] overflow-y-auto custom-scrollbar">
        <div class="flex justify-between items-start">
          <span class="bg-rose-50 text-rose-600 text-xs font-bold px-3 py-1.5 rounded-lg border border-rose-200 shadow-sm">🎆 지역 축제·행사</span>
          <button @click="closeFestivalDetail" class="text-slate-400 hover:text-slate-600 w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 transition font-bold text-lg">✕</button>
        </div>

        <h3 class="text-2xl font-extrabold text-slate-800 tracking-tight">{{ selectedFestival.title }}</h3>

        <div v-if="selectedFestival.image" class="relative group">
          <img :src="selectedFestival.image" @click="openFullImage(selectedFestival.image)" class="w-full h-64 object-cover rounded-2xl shadow-sm border border-slate-100 cursor-zoom-in group-hover:opacity-95 transition">
          <div class="absolute bottom-3 right-3 bg-black/50 text-white text-[10px] px-2 py-1 rounded-md pointer-events-none">클릭하여 확대</div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-slate-600 bg-slate-50 p-5 rounded-2xl border border-slate-100">
          <p><span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">📅 기간</span> {{ selectedFestival.date_start }} ~ {{ selectedFestival.date_end }}</p>
          <p v-if="selectedFestival.place"><span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">📍 장소</span> {{ selectedFestival.place }}</p>
          <p v-if="selectedFestival.address"><span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">🏠 주소</span> {{ selectedFestival.address }}</p>
          <p v-if="selectedFestival.playtime"><span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">🕐 시간</span> {{ selectedFestival.playtime }}</p>
          <p v-if="selectedFestival.fee"><span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">💰 요금</span> {{ selectedFestival.fee }}</p>
          <p v-if="selectedFestival.tel"><span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">📞 전화</span> {{ selectedFestival.tel }}</p>
          <p v-if="selectedFestival.eventhomepage" class="sm:col-span-2 break-all">
            <span class="font-bold text-slate-800 mr-1 text-xs bg-white px-2 py-1 rounded shadow-sm">🔗 홈페이지</span>
            <a :href="selectedFestival.eventhomepage" target="_blank" rel="noopener noreferrer" class="text-sky-600 hover:underline font-medium ml-1">{{ selectedFestival.eventhomepage }}</a>
          </p>
        </div>

        <div v-if="selectedFestival.subevent" class="bg-slate-50 p-4 rounded-2xl border border-slate-100">
          <p class="font-bold text-slate-800 text-sm mb-2 flex items-center"><span class="mr-1">➕</span> 부대행사</p>
          <p class="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{{ selectedFestival.subevent }}</p>
        </div>

        <div v-if="selectedFestival.program" class="bg-slate-50 p-4 rounded-2xl border border-slate-100">
          <p class="font-bold text-slate-800 text-sm mb-2 flex items-center"><span class="mr-1">📋</span> 프로그램</p>
          <p class="text-sm text-slate-600 whitespace-pre-wrap leading-relaxed">{{ selectedFestival.program }}</p>
        </div>
      </div>
    </div>

    <!-- [모달 2]: 라이트박스 이미지 풀사이즈 보기 -->
    <div v-if="fullImageUrl" @click="closeFullImage" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/90 cursor-zoom-out animate-fade-in">
      <img :src="fullImageUrl" class="max-w-full max-h-full rounded-2xl shadow-2xl border border-white/10">
      <button @click="closeFullImage" class="absolute top-6 right-6 text-white/70 hover:text-white w-10 h-10 bg-white/10 rounded-full flex items-center justify-center text-xl transition backdrop-blur-sm">✕</button>
    </div>
  </div>
</template>

<script setup>
import api from '../api';
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue';
import Chart from 'chart.js/auto';
import * as d3 from 'd3';

const props = defineProps({
  posts: {
    type: Array,
    required: true
  }
});

const categoryChartRef = ref(null);
const regionChartRef = ref(null);
const regionStatsRef = ref(null);

let categoryChartInstance = null;
let regionChartInstance = null;

const regionKeywords = {
  '해운대·광안리': ['해운대', '광안리', '센텀', '마린시티'],
  '중구·남포동': ['남포동', '중구', '국제시장', '자갈치', '부산역'],
  '영도': ['영도', '영도구'],
  '동래·온천장': ['동래', '온천장', '연제', '사직'],
  '서면': ['서면', '부전', '전포'],
  '기장': ['기장', '정관', '오시리아'],
  '사하·감천': ['감천', '사하', '신평', '하단'],
};

const getRegionLabel = (post) => {
  const text = `${post.title || ''} ${post.content || ''}`.toLowerCase();
  for (const [region, keywords] of Object.entries(regionKeywords)) {
    if (keywords.some(keyword => text.includes(keyword))) return region;
  }
  return '기타';
};

const buildRegionChartData = () => {
  const counts = {};
  props.posts.forEach(post => {
    const region = getRegionLabel(post);
    counts[region] = (counts[region] || 0) + 1;
  });
  return Object.entries(counts)
    .map(([label, count]) => ({ label, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);
};

const buildPopularRegionData = () => {
  const metrics = {};
  props.posts.forEach(post => {
    const region = getRegionLabel(post);
    if (!metrics[region]) metrics[region] = { label: region, posts: 0, likes: 0, views: 0 };
    metrics[region].posts += 1;
    metrics[region].likes += post.likes || 0;
    metrics[region].views += post.views || 0;
  });
  return Object.values(metrics)
    .map(item => ({ ...item, score: item.likes * 2 + item.views * 0.3 }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 6);
};

const renderD3RegionStats = () => {
  const container = regionStatsRef.value;
  if (!container) return;
  container.innerHTML = '';
  const stats = buildPopularRegionData();
  if (!stats.length) {
    container.innerHTML = '<div class="text-xs text-slate-400 flex items-center justify-center h-full">통계 데이터가 아직 없어요.</div>';
    return;
  }
  
  const width = container.clientWidth || 260;
  const height = 220;
  const margin = { top: 10, right: 16, bottom: 24, left: 90 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const svg = d3.select(container)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', `0 0 ${width} ${height}`);

  const x = d3.scaleLinear()
    .domain([0, d3.max(stats, item => item.score) + 10])
    .range([0, innerWidth]);

  const y = d3.scaleBand()
    .domain(stats.map(item => item.label))
    .range([0, innerHeight])
    .padding(0.2);

  const g = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

  g.selectAll('rect')
    .data(stats)
    .join('rect')
    .attr('x', 0)
    .attr('y', item => y(item.label))
    .attr('width', item => x(item.score))
    .attr('height', y.bandwidth())
    .attr('rx', 8)
    .attr('fill', '#0ea5e9');

  g.append('g')
    .call(d3.axisLeft(y).tickSize(0))
    .call(g => g.selectAll('text').attr('fill', '#0f4c81').attr('font-size', 11));

  g.append('g')
    .attr('transform', `translate(0, ${innerHeight})`)
    .call(d3.axisBottom(x).ticks(4).tickFormat(value => `${value}`))
    .call(g => g.selectAll('text').attr('fill', '#64748b').attr('font-size', 10));

  g.selectAll('.tick line').attr('stroke', '#dbeafe');
};

const updateCharts = () => {
  if (categoryChartInstance && props.posts.length) {
    const counts = [
      props.posts.filter(p => p.category === '관광지').length,
      props.posts.filter(p => p.category === '맛집').length,
      props.posts.filter(p => p.category === '축제·행사').length,
      props.posts.filter(p => p.category === '자유').length,
    ];
    categoryChartInstance.data.datasets[0].data = counts;
    categoryChartInstance.update();
  }
  // D3 및 Region Chart 업데이트 로직 실행...
  if (regionChartInstance) {
    const regionData = buildRegionChartData(); // 이미 정의하신 buildRegionChartData 사용
    regionChartInstance.data.labels = regionData.map(item => item.label);
    regionChartInstance.data.datasets[0].data = regionData.map(item => item.count);
    regionChartInstance.update();
  }

  // 지역 차트
  renderD3RegionStats();
};


const festivalCalendarRef = ref(null);
const hoveredEvent = ref(null);
const selectedFestival = ref(null); // 클릭 시 상세 정보를 담을 변수
const fullImageUrl = ref(null);
let calendarInstance = null;

const closeFestivalDetail = () => { selectedFestival.value = null; };
const openFullImage = (url) => { if (url) fullImageUrl.value = url; };
const closeFullImage = () => { fullImageUrl.value = null; };

const CALENDAR_COLORS = [
  '#0f4c81', '#0ea5e9', '#f97316', '#16a34a', '#a855f7',
  '#e11d48', '#0d9488', '#ca8a04', '#6366f1', '#db2777',
];

const colorForEvent = (key) => {
  let hash = 0;
  for (let i = 0; i < key.length; i++) hash = (hash * 31 + key.charCodeAt(i)) % CALENDAR_COLORS.length;
  return CALENDAR_COLORS[Math.abs(hash) % CALENDAR_COLORS.length];
};

const positionTooltip = (clientX, clientY) => {
  if (!hoveredEvent.value || !festivalCalendarRef.value) return;
  const containerRect = festivalCalendarRef.value.parentElement.getBoundingClientRect();
  const offset = 6;
  const tooltipWidth = 272;
  const tooltipHeight = 260;
  let x = clientX - containerRect.left + offset;
  let y = clientY - containerRect.top + offset;
  
  if (x + tooltipWidth > containerRect.width) x = clientX - containerRect.left - tooltipWidth - offset;
  if (y + tooltipHeight > containerRect.height) y = clientY - containerRect.top - tooltipHeight - offset;
  
  hoveredEvent.value.x = Math.max(8, x);
  hoveredEvent.value.y = Math.max(8, y);
};

const handleMouseMove = (jsEvent) => {
  if (hoveredEvent.value) positionTooltip(jsEvent.clientX, jsEvent.clientY);
};

const initCalendar = async () => {
  await nextTick();

  // 1. 여기서 ref(festivalCalendarRef)를 직접 사용합니다.
  const calendarEl = festivalCalendarRef.value;
  if (!calendarEl || calendarInstance) return;

  if (!window.FullCalendar) {
    console.error("🚨 FullCalendar 라이브러리를 찾을 수 없습니다. index.html의 CDN을 확인하세요.");
    return;
  }

  let events = [];
  try {
    const response = await api.get('/api/public-data/festivals');
    console.log("🎉 서버에서 받아온 축제 데이터 개수:", response.data.length, response.data);

    events = response.data.map(event => ({
      id: event.id,
      title: event.title,
      start: event.start,
      end: event.end,
      color: colorForEvent(String(event.id || event.title)),
      extendedProps: { ...event },
    }));
  } catch (error) { console.error(error); }

  // FullCalendar는 window 객체에 전역으로 로드되어 있어야 함 (CDN 사용 시)
  calendarInstance = new window.FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'ko',
    height: 'auto',
    events,
    eventMouseEnter: (info) => {
      const props = info.event.extendedProps;
      hoveredEvent.value = {
        title: info.event.title,
        place: props.place,
        fee: props.fee,
        playtime: props.playtime,
        image: props.image || '',
        x: 0, y: 0,
      };
      positionTooltip(info.jsEvent.clientX, info.jsEvent.clientY);
    },
    eventMouseLeave: () => { hoveredEvent.value = null; },
    eventClick: (info) => {
      hoveredEvent.value = null;
      selectedFestival.value = { title: info.event.title, ...info.event.extendedProps };
    },
  });
  calendarInstance.render();
};

onMounted(() => {

    // 카테고리 차트 
  if (categoryChartRef.value) {
    categoryChartInstance = new Chart(categoryChartRef.value, {
      type: 'doughnut',
      data: {
        labels: ['🏝️ 관광지', '🍲 맛집', '🎪 축제·행사', '💬 자유'],
        datasets: [{
          data: [2, 3, 1, 1],
          backgroundColor: ['#0f4c81', '#0284c7', '#38bdf8', '#bae6fd'],
          borderColor: '#ffffff',
          borderWidth: 2,
        }]
      },
      options: { 
        responsive: true, 
        maintainAspectRatio: false, 
        plugins: { legend: { position: 'right', labels: { font: { family: 'sans-serif', size: 11 } } } },
        cutout: '65%' }
    });
  }

  // 권역 차트
  if (regionChartRef.value) {
    regionChartInstance = new Chart(regionChartRef.value, {
      type: 'bar',
      data: {
        labels: [],
        datasets: [{
          label: '게시글 수',
          data: [],
          backgroundColor: ['#38bdf8', '#0ea5e9', '#0284c7', '#0f4c81', '#7dd3fc', '#bae6fd'],
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { color: '#64748b' },
            grid: { color: 'rgba(148, 163, 184, 0.2)' }
          },
          x: {
            ticks: { color: '#64748b' },
            grid: { display: false }
          }
        }
      }
    });
  }
  
  updateCharts();
  document.addEventListener('mousemove', handleMouseMove);
  initCalendar();
});

watch(() => props.posts, () => {
  updateCharts();
}, { deep: true });

onUnmounted(() => {
  window.removeEventListener('resize', renderD3RegionStats);
  if (categoryChartInstance) categoryChartInstance.destroy();
  if (regionChartInstance) regionChartInstance.destroy();

  document.removeEventListener('mousemove', handleMouseMove);
  if (calendarInstance) calendarInstance.destroy();
});
</script>