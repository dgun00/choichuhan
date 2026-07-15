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
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue';
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
});

watch(() => props.posts, () => {
  updateCharts();
}, { deep: true });

onUnmounted(() => {
  window.removeEventListener('resize', renderD3RegionStats);
  if (categoryChartInstance) categoryChartInstance.destroy();
  if (regionChartInstance) regionChartInstance.destroy();
});

</script>