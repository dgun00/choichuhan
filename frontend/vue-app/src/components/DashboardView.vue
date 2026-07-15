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
import { ref, onMounted, watch } from 'vue';
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
};

onMounted(() => {
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
      options: { responsive: true, maintainAspectRatio: false, cutout: '65%' }
    });
  }
  updateCharts();
});

watch(() => props.posts, updateCharts, { deep: true });
</script>