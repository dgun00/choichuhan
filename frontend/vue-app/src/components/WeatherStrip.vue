<template>
  <div class="space-y-6">
    <div class="glass-card rounded-3xl p-6 sm:p-8">
      <div class="flex flex-col sm:flex-row justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-cerulean-900 flex items-center"><span class="mr-2">🌦️</span> 부산 권역 여행날씨</h2>
          <p class="text-sm text-slate-600 mt-1">권역별 현재 날씨와 여행 적합도를 한눈에 확인해 보세요.</p>
        </div>
        <div class="text-xs text-slate-500 bg-white/70 px-3 py-2 rounded-xl">실시간 기상 정보 기반 · 외부 API 연동</div>
      </div>
    </div>

    <div v-if="weatherLoading" class="glass-card rounded-3xl p-8 text-center text-sm text-slate-500">날씨 정보를 불러오는 중입니다...</div>
    <div v-else-if="weatherRegions.length === 0" class="glass-card rounded-3xl p-8 text-center text-sm text-slate-500">날씨 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.</div>
    <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <div v-for="region in weatherRegions" :key="region.id" @click="openWeatherDetail(region)" class="glass-card rounded-3xl p-5 space-y-4 cursor-pointer hover:shadow-xl transition">
        <div class="flex items-start justify-between gap-2">
          <div>
            <h3 class="font-bold text-cerulean-900">{{ region.name }}</h3>
            <p class="text-xs text-slate-500 mt-1">{{ region.current_weather.weatherlabel }}</p>
          </div>
          <span :class="getSuitabilityBadgeClass(region.travel_suitability.level)" class="px-2.5 py-1 rounded-full text-[11px] font-semibold shrink-0">{{ region.travel_suitability.level }}</span>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm text-slate-700">
          <div class="bg-white/70 rounded-xl p-3">
            <div class="text-[11px] text-slate-500">🌡️ 기온</div>
            <div class="font-semibold mt-1">{{ region.current_weather.temperature }}℃</div>
          </div>
          <div class="bg-white/70 rounded-xl p-3">
            <div class="text-[11px] text-slate-500">💧 습도</div>
            <div class="font-semibold mt-1">{{ region.current_weather.humidity }}%</div>
          </div>
          <div class="bg-white/70 rounded-xl p-3">
            <div class="text-[11px] text-slate-500">🌧️ 강수</div>
            <div class="font-semibold mt-1">{{ region.current_weather.precipitation }}mm</div>
          </div>
          <div class="bg-white/70 rounded-xl p-3">
            <div class="text-[11px] text-slate-500">💨 풍속</div>
            <div class="font-semibold mt-1">{{ region.current_weather.windspeed }}m/s</div>
          </div>
        </div>

        <div class="rounded-2xl border border-white/80 bg-white/60 p-3">
          <div class="flex items-center justify-between text-sm font-semibold text-slate-700">
            <span>여행 적합도</span>
            <span class="text-cerulean-700">{{ region.travel_suitability.score }}/100</span>
          </div>
          <p class="text-xs text-slate-500 mt-1">{{ region.travel_suitability.summary }}</p>
          <div class="flex flex-wrap gap-2 mt-3">
            <span v-for="reason in region.travel_suitability.reasons" :key="reason" class="text-[11px] bg-cerulean-50 text-cerulean-700 px-2 py-1 rounded-full border border-cerulean-100">{{ reason }}</span>
            <span v-if="region.travel_suitability.reasons.length === 0" class="text-[11px] bg-cerulean-50 text-cerulean-700 px-2 py-1 rounded-full border border-cerulean-100">날씨가 비교적 안정적이에요</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Weather detail modal -->
    <div v-if="selectedWeatherRegion" @click.self="closeWeatherDetail" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
      <div class="glass-modal w-full max-w-xl rounded-3xl p-6 shadow-2xl border border-white space-y-5">
        <div class="flex justify-between items-start gap-3">
          <div>
            <h3 class="text-xl font-bold text-cerulean-900">{{ selectedWeatherRegion.name }}</h3>
            <p class="text-sm text-slate-500 mt-1">현재 권역의 실시간 날씨와 여행 추천 상황입니다.</p>
          </div>
          <button @click="closeWeatherDetail" class="text-slate-400 hover:text-slate-600 font-bold text-lg">✕</button>
        </div>

        <div class="rounded-2xl bg-gradient-to-br from-cerulean-50 to-sky-50 p-4 border border-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-semibold text-cerulean-700">현재 상태</p>
              <p class="text-3xl font-black text-cerulean-900 mt-1">{{ selectedWeatherRegion.current_weather.weatherlabel }}</p>
            </div>
            <span :class="getSuitabilityBadgeClass(selectedWeatherRegion.travel_suitability.level)" class="px-3 py-2 rounded-full text-sm font-semibold">{{ selectedWeatherRegion.travel_suitability.level }}</span>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3 text-sm">
          <div class="bg-white/70 rounded-2xl p-3 border border-white">
            <p class="text-[11px] text-slate-500">🌡️ 기온</p>
            <p class="font-semibold text-slate-700 mt-1">{{ selectedWeatherRegion.current_weather.temperature }}℃</p>
          </div>
          <div class="bg-white/70 rounded-2xl p-3 border border-white">
            <p class="text-[11px] text-slate-500">💧 습도</p>
            <p class="font-semibold text-slate-700 mt-1">{{ selectedWeatherRegion.current_weather.humidity }}%</p>
          </div>
          <div class="bg-white/70 rounded-2xl p-3 border border-white">
            <p class="text-[11px] text-slate-500">🌧️ 강수량</p>
            <p class="font-semibold text-slate-700 mt-1">{{ selectedWeatherRegion.current_weather.precipitation }}mm</p>
          </div>
          <div class="bg-white/70 rounded-2xl p-3 border border-white">
            <p class="text-[11px] text-slate-500">💨 풍속</p>
            <p class="font-semibold text-slate-700 mt-1">{{ selectedWeatherRegion.current_weather.windspeed }}m/s</p>
          </div>
        </div>

        <div class="rounded-2xl border border-cerulean-100 bg-white/70 p-4">
          <div class="flex items-center justify-between">
            <p class="text-sm font-semibold text-slate-700">여행 적합도</p>
            <p class="text-lg font-black text-cerulean-700">{{ selectedWeatherRegion.travel_suitability.score }}/100</p>
          </div>
          <p class="text-sm text-slate-600 mt-2">{{ selectedWeatherRegion.travel_suitability.summary }}</p>
          <div class="flex flex-wrap gap-2 mt-3">
            <span v-for="reason in selectedWeatherRegion.travel_suitability.reasons" :key="reason" class="text-[11px] bg-cerulean-50 text-cerulean-700 px-2 py-1 rounded-full border border-cerulean-100">{{ reason }}</span>
            <span v-if="selectedWeatherRegion.travel_suitability.reasons.length === 0" class="text-[11px] bg-cerulean-50 text-cerulean-700 px-2 py-1 rounded-full border border-cerulean-100">날씨가 비교적 안정적이에요</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const weatherRegions = ref([]);
const weatherLoading = ref(true);
const selectedWeatherRegion = ref(null);

const getSuitabilityBadgeClass = (level) => {
  switch (level) {
    case '좋음': return 'bg-emerald-100 text-emerald-700 border border-emerald-200';
    case '보통': return 'bg-sky-100 text-sky-700 border border-sky-200';
    case '주의': return 'bg-amber-100 text-amber-700 border border-amber-200';
    default: return 'bg-rose-100 text-rose-700 border border-rose-200';
  }
};

const loadWeatherRegions = async () => {
  weatherLoading.value = true;
  try {
    const resp = await api.get('/api/weather/regions');
    const data = resp.data;
    weatherRegions.value = data.regions || [];
  } catch (error) {
    weatherRegions.value = [];
    console.error('loadWeatherRegions error', error);
  } finally {
    weatherLoading.value = false;
  }
};

const openWeatherDetail = (region) => {
  selectedWeatherRegion.value = region;
};

const closeWeatherDetail = () => {
  selectedWeatherRegion.value = null;
};

onMounted(() => {
  loadWeatherRegions();
});
</script>

<style scoped>
/* Component assumes Tailwind + project glass utilities are available globally. */
</style>
