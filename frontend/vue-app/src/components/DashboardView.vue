<template>
  <div class="space-y-6 animate-fade-in">
    <!-- 권역 소개 글래스 배너 -->
    <div class="glass-card rounded-3xl p-8 relative overflow-hidden">
      <div class="max-w-xl">
        <span class="bg-cerulean-100 text-cerulean-800 text-xs font-bold px-3 py-1 rounded-full border border-cerulean-300">
          ✨ 공공데이터 100% 연동
        </span>
        <h2 class="text-2xl sm:text-3xl font-extrabold text-cerulean-900 mt-3 leading-tight">
          부산 권역 실시간 지역 정보 & 익명 커뮤니티
        </h2>
        <p class="text-slate-600 text-sm mt-2">
          로그인 없이 자유롭게 맛집, 관광지, 축제 정보를 나누고 AI 챗봇에게 무엇이든 물어보세요!
        </p>
      </div>
    </div>

    <!-- 통계 차트 그리드 -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
      <div class="glass-card p-6 rounded-2xl">
        <h3 class="text-base font-bold text-cerulean-900 flex items-center mb-4"><span class="mr-2">📈</span> 카테고리별 게시글 현황</h3>
        <div class="h-64 flex justify-center items-center">
          <canvas ref="categoryChartRef"></canvas>
        </div>
      </div>
      <div class="glass-card p-6 rounded-2xl">
        <h3 class="text-base font-bold text-cerulean-900 flex items-center mb-4"><span class="mr-2">📍</span> 권역별 게시글 현황</h3>
        <div class="h-64 flex justify-center items-center">
          <canvas ref="regionChartRef"></canvas>
        </div>
      </div>
      <div class="glass-card p-6 rounded-2xl">
        <h3 class="text-base font-bold text-cerulean-900 flex items-center mb-4"><span class="mr-2">🏆</span> 인기 지역 통계</h3>
        <div ref="regionStatsRef" class="h-64 w-full"></div>
      </div>
    </div>

    <!-- 축제 캘린더 영역 -->
    <div class="glass-card p-6 rounded-2xl relative mt-6">
      <h3 class="text-base font-bold text-cerulean-900 flex items-center mb-4">
        <span class="mr-2">📅</span> 부산 축제·행사 캘린더
      </h3>
      <div ref="festivalCalendarRef" class="bg-white/70 rounded-2xl p-3 border border-white min-h-[450px]"></div>
      
      <!-- 툴팁 (마우스 오버시 정보) -->
      <div v-if="hoveredEvent" class="absolute z-50 w-64 bg-white rounded-2xl shadow-2xl border border-cerulean-100 p-3 text-xs space-y-1.5 pointer-events-none animate-fade-in"
              :style="{ left: hoveredEvent.x + 'px', top: hoveredEvent.y + 'px' }">
        <img v-if="hoveredEvent.image" :src="hoveredEvent.image" class="w-full h-28 object-cover rounded-xl mb-1">
            <p class="font-bold text-slate-800 leading-snug">{{ hoveredEvent.title }}</p>
            <p class="text-slate-500">📍 {{ hoveredEvent.place || '장소 정보 없음' }}</p>
            <p class="text-slate-500">🕐 {{ hoveredEvent.playtime || '운영시간 정보 없음' }}</p>
            <p class="text-slate-500">💰 {{ hoveredEvent.fee || '요금 정보 없음' }}</p>
      </div>
    </div>

    <!-- [모달 1]: 축제·행사 상세 정보 모달 -->
    <div v-if="selectedFestival" @click.self="closeFestivalDetail" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div @click.stop class="glass-modal w-full max-w-2xl rounded-3xl p-6 shadow-2xl border border-white space-y-4 max-h-[85vh] overflow-y-auto">
        <div class="flex justify-between items-start">
          <span class="bg-cerulean-100 text-cerulean-800 text-xs font-semibold px-2.5 py-1 rounded-md">🎪 축제·행사</span>
          <button @click="closeFestivalDetail" class="text-slate-400 hover:text-slate-600 font-bold text-lg">✕</button>
        </div>

        <h3 class="text-xl font-bold text-slate-800">{{ selectedFestival.title }}</h3>

        <!-- 대표 이미지 (클릭하면 풀사이즈로 보기) -->
        <div v-if="selectedFestival.image" class="relative">
          <img :src="selectedFestival.image" @click="openFullImage(selectedFestival.image)" class="w-full h-56 object-cover rounded-2xl border border-white cursor-zoom-in hover:opacity-90 transition">
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm text-slate-600 bg-white/60 p-4 rounded-2xl border border-white">
          <p><span class="font-semibold text-slate-700">📅 기간</span> {{ selectedFestival.date_start }} ~ {{ selectedFestival.date_end }}</p>
          <p v-if="selectedFestival.place"><span class="font-semibold text-slate-700">📍 장소</span> {{ selectedFestival.place }}</p>
          <p v-if="selectedFestival.address"><span class="font-semibold text-slate-700">🏠 주소</span> {{ selectedFestival.address }}</p>
          <p v-if="selectedFestival.playtime"><span class="font-semibold text-slate-700">🕐 운영시간</span> {{ selectedFestival.playtime }}</p>
          <p v-if="selectedFestival.fee"><span class="font-semibold text-slate-700">💰 요금</span> {{ selectedFestival.fee }}</p>
          <p v-if="selectedFestival.tel"><span class="font-semibold text-slate-700">📞 전화</span> {{ selectedFestival.tel }}</p>
          <p v-if="selectedFestival.eventhomepage" class="sm:col-span-2 break-all">
            <span class="font-semibold text-slate-700">🔗 홈페이지</span>
            <a :href="selectedFestival.eventhomepage" target="_blank" rel="noopener noreferrer" class="text-cerulean-700 hover:underline">{{ selectedFestival.eventhomepage }}</a>
          </p>
        </div>

        <div v-if="selectedFestival.subevent" class="bg-white/60 p-4 rounded-2xl border border-white">
          <p class="font-semibold text-slate-700 text-sm mb-1">➕ 부대행사</p>
          <p class="text-sm text-slate-600 whitespace-pre-wrap">{{ selectedFestival.subevent }}</p>
        </div>

        <div v-if="selectedFestival.program" class="bg-white/60 p-4 rounded-2xl border border-white">
          <p class="font-semibold text-slate-700 text-sm mb-1">📋 프로그램</p>
          <p class="text-sm text-slate-600 whitespace-pre-wrap">{{ selectedFestival.program }}</p>
        </div>
      </div>
    </div>

    <!-- [모달 2]: 라이트박스 이미지 풀사이즈 보기 -->
    <div v-if="fullImageUrl" @click="closeFullImage" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 cursor-zoom-out animate-fade-in">
      <img :src="fullImageUrl" class="max-w-full max-h-full rounded-2xl shadow-2xl">
      <button @click="closeFullImage" class="absolute top-4 right-4 text-white/80 hover:text-white text-2xl font-bold">✕</button>
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