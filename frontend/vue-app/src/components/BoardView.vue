<template>
  <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-6">
    <!-- 상단 헤더 & 글쓰기 버튼 -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h2 class="text-xl font-bold text-cerulean-900 flex items-center"><span class="mr-2">💬</span> 부산 권역 자유 커뮤니티</h2>
        <p class="text-xs text-slate-500 mt-1">※ 회원가입 없이 평문 비밀번호로 게시글을 관리합니다.</p>
      </div>
      <button @click="showWriteModal = true" class="bg-cerulean-700 hover:bg-cerulean-800 text-white font-medium px-5 py-2.5 rounded-xl shadow-md transition flex items-center text-sm shrink-0">
        <span class="mr-1">✏️</span> 새 글 작성
      </button>
    </div>

    <!-- 카테고리 필터 & 검색바 -->
    <div class="flex flex-col md:flex-row justify-between gap-4 bg-white/40 p-2.5 rounded-2xl border border-white/60 backdrop-blur-sm">
      <div class="flex flex-wrap gap-2">
        <button v-for="cat in categories" :key="cat" @click="selectedCategory = cat" 
          :class="selectedCategory === cat ? 'bg-sky-500 text-white font-bold shadow-md shadow-sky-500/20 border-transparent' : 'bg-white/70 text-slate-600 hover:bg-white border-white/60'" 
          class="px-4 py-2 rounded-xl text-xs transition-all flex items-center gap-1.5 border backdrop-blur-md">
          <span class="text-sm drop-shadow-sm">{{ getCategoryIcon(cat) }}</span> {{ cat }}
        </button>
      </div>
      <div class="relative w-full md:w-64">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">🔍</span>
        <input v-model="searchKeyword" type="text" placeholder="어떤 정보가 궁금하신가요?" class="w-full bg-white/80 border border-white rounded-xl pl-9 pr-4 py-2.5 text-xs focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 transition-all font-medium placeholder-slate-400 shadow-inner">
      </div>
    </div>

    <!-- 트렌디한 게시글 목록 테이블 -->
    <div class="overflow-x-auto rounded-2xl border border-white/50 bg-white/30 backdrop-blur-sm">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="text-slate-500 text-xs uppercase tracking-wider border-b-2 border-white/60 bg-white/40">
            <th class="py-4 px-4 font-bold w-16 text-center">NO</th>
            <th class="py-4 px-4 font-bold w-32">카테고리</th>
            <th class="py-4 px-4 font-bold">제목</th>
            <th class="py-4 px-4 font-bold w-24 text-center">조회</th>
            <th class="py-4 px-4 font-bold w-24 text-center">반응</th>
          </tr>
        </thead>
        <tbody class="text-sm divide-y divide-white/40">
          <tr v-for="post in filteredPosts" :key="post.id" @click="openDetail(post)" class="hover:bg-white/70 transition-colors cursor-pointer group">
            <td class="py-4 px-4 text-center text-slate-400 font-bold text-xs">{{ post.id }}</td>
            <td class="py-4 px-4">
              <span class="bg-blue-50/70 backdrop-blur-sm text-sky-700 text-[11px] font-bold px-2.5 py-1 rounded-lg border border-blue-200/50 shadow-sm">
                {{ getCategoryIcon(post.category) }} {{ post.category }}
              </span>
            </td>
            <td class="py-4 px-4 font-bold text-slate-700 group-hover:text-sky-600 transition-colors truncate max-w-[200px] sm:max-w-md">
              {{ post.title }}
            </td>
            <td class="py-4 px-4 text-center text-xs font-medium text-slate-500">{{ post.views }}</td>
            <td class="py-4 px-4 text-center">
              <span class="inline-flex items-center text-xs font-bold text-pink-500 bg-pink-50/70 backdrop-blur-sm px-2.5 py-1 rounded-full border border-pink-100/50 shadow-sm">
                🌺 {{ post.likes }}
              </span>
            </td>
          </tr>
          <tr v-if="filteredPosts.length === 0">
            <td colspan="5" class="py-20 text-center text-slate-400">
              <div class="text-5xl mb-4 opacity-50 drop-shadow-md">🏖️</div>
              <p class="text-sm font-bold text-slate-500">아직 등록된 정보가 없어요. 첫 글의 주인공이 되어보세요!</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

 <!-- 모달 1: 게시글 작성 창 -->
<div v-if="showWriteModal" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/30 backdrop-blur-sm animate-fade-in">
  <div class="bg-white/95 backdrop-blur-2xl w-full max-w-lg rounded-[2rem] p-8 shadow-2xl border border-white space-y-5">
    <h3 class="text-xl font-bold text-slate-800 flex items-center border-b border-slate-200/60 pb-3">
      <span class="mr-2 text-2xl">✍️</span> 로컬 정보 나누기
    </h3>
    <div class="space-y-4 text-sm">
      <div>
        <label class="block text-xs font-bold text-slate-500 mb-1.5 ml-1">카테고리</label>
        <select v-model="newPost.category" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-sky-400/50 outline-none transition-all font-medium text-slate-700 shadow-inner">
          <option v-for="cat in categories.slice(1)" :key="cat" :value="cat">{{ getCategoryIcon(cat) }} {{ cat }}</option>
        </select>
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-500 mb-1.5 ml-1">제목</label>
        <input v-model="newPost.title" type="text" placeholder="어떤 유용한 정보를 공유하실 건가요?" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-sky-400/50 outline-none transition-all shadow-inner">
      </div>
      <div>
        <label class="block text-xs font-bold text-slate-500 mb-1.5 ml-1">내용</label>
        <textarea v-model="newPost.content" rows="4" placeholder="현지인만 아는 꿀팁을 자유롭게 적어주세요!" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-sky-400/50 outline-none transition-all resize-none shadow-inner"></textarea>
      </div>
      <div>
        <label class="block text-xs font-bold text-rose-500 mb-1.5 ml-1">비밀번호 (수정/삭제용 평문)</label>
        <input v-model="newPost.password" type="password" placeholder="기억하기 쉬운 숫자 4자리" class="w-full bg-rose-50/50 border border-rose-200 rounded-2xl px-4 py-3 text-sm focus:ring-2 focus:ring-rose-400/50 outline-none transition-all text-rose-600 placeholder-rose-300 font-bold shadow-inner">
      </div>
    </div>
    <div class="flex justify-end space-x-2 pt-4">
      <button @click="showWriteModal = false" class="px-5 py-2.5 rounded-xl bg-slate-100 text-slate-600 font-bold text-sm hover:bg-slate-200 transition">취소</button>
      <button @click="submitPost" class="px-6 py-2.5 rounded-xl bg-sky-500 text-white font-bold text-sm hover:bg-sky-600 transition shadow-md">등록하기</button>
    </div>
  </div>
</div>

<!-- 모달 2: 게시글 상세 & 비밀번호 확인 창 -->
<div v-if="selectedPost" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-slate-900/30 backdrop-blur-sm animate-fade-in">
  <div class="bg-white/95 backdrop-blur-2xl w-full max-w-xl rounded-[2rem] p-6 sm:p-8 shadow-2xl border border-white space-y-5">
    <div class="flex justify-between items-start">
      <span class="bg-blue-50/80 text-sky-700 text-xs font-bold px-3 py-1.5 rounded-lg border border-blue-200/60 shadow-sm">
        {{ getCategoryIcon(selectedPost.category) }} {{ selectedPost.category }}
      </span>
      <button @click="selectedPost = null; pwdMode = null" class="text-slate-400 hover:text-slate-600 font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 transition text-lg">✕</button>
    </div>
    
    <h3 class="text-2xl font-extrabold text-slate-800 tracking-tight">{{ selectedPost.title }}</h3>
    
    <div class="min-h-[8rem] bg-slate-50/80 p-5 rounded-2xl text-slate-700 text-sm leading-relaxed whitespace-pre-wrap border border-slate-100 shadow-inner">
      {{ selectedPost.content }}
    </div>
    
    <div class="flex justify-between items-center text-xs pt-2">
      <span class="text-slate-400 font-bold bg-white/50 px-3 py-1.5 rounded-full border border-slate-100 shadow-sm">👁️ 조회수 {{ selectedPost.views }}</span>
      <button @click="likeSelected" class="px-4 py-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-pink-600 font-bold transition flex items-center space-x-1.5 border border-rose-100 shadow-sm">
        <span class="text-base">🌺</span> <span>도움돼요 {{ selectedPost.likes }}</span>
      </button>
    </div>

    <div v-if="!pwdMode" class="flex justify-end space-x-2 pt-4 border-t border-slate-100">
      <button @click="pwdMode = 'edit'" class="px-5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition">수정</button>
      <button @click="pwdMode = 'delete'" class="px-5 py-2 bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-600 rounded-xl text-xs font-bold transition">삭제</button>
    </div>

    <!-- 비밀번호 확인 영역 -->
    <div v-else class="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-3 mt-4 animate-fade-in shadow-inner">
      <p class="text-xs font-bold text-slate-700 flex items-center"><span class="mr-1">🔒</span> {{ pwdMode === 'edit' ? '수정' : '삭제' }} 권한 확인</p>
      <div class="flex space-x-2">
        <input v-model="inputPwd" type="password" placeholder="비밀번호 입력" class="flex-1 bg-white border border-slate-300 rounded-xl px-3 py-2 text-sm outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20">
        <button @click="verifyPassword" class="px-5 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold shadow hover:bg-slate-700 transition">확인</button>
        <button @click="pwdMode = null; inputPwd = ''" class="px-4 py-2 bg-slate-200 text-slate-600 rounded-xl text-xs font-bold hover:bg-slate-300 transition">취소</button>
      </div>
    </div>
  </div>
</div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import api from '../api'; // 새로 만든 axios 인스턴스

const emit = defineEmits(['refresh-posts', 'open-detail']);

const props = defineProps({
  posts: { type: Array, required: true }
});

const showWriteModal = ref(false);
const selectedPost = ref(null);
const pwdMode = ref(null);
const inputPwd = ref('');
const searchKeyword = ref('');
const selectedCategory = ref('전체');

const categories = ['전체', '관광지', '맛집', '축제·행사', '자유'];

const getCategoryIcon = (cat) => {
  switch(cat) {
    case '관광지': return '🏝️';
    case '맛집': return '🍲';
    case '축제·행사': return '🎪';
    case '자유': return '💬';
    default: return '🌈';
  }
};

const newPost = ref({ category: '맛집', title: '', content: '', password: '' });
const comments = ref([]);
const newComment = ref({ content: '', password: '' });

const filteredPosts = computed(() => {
  return props.posts.filter(p => {
    const matchCat = selectedCategory.value === '전체' || p.category === selectedCategory.value;
    const matchKey = p.title.includes(searchKeyword.value) || p.content.includes(searchKeyword.value);
    return matchCat && matchKey;
  });
});

const submitPost = async () => {
  if (!newPost.value.title || !newPost.value.content || !newPost.value.password) {
    alert('제목, 내용, 비밀번호를 모두 입력해 주세요!');
    return;
  }
  try {
    const res = await api.post('/api/posts', newPost.value);
    // 성공하면 부모에게 갱신 요청
    emit('refresh-posts');
    newPost.value = { category: '맛집', title: '', content: '', password: '' };
    showWriteModal.value = false;
  } catch (err) {
    const msg = err?.response?.data?.detail || '게시글 등록에 실패했습니다.';
    alert(msg);
  }
};

const openDetail = async (post) => {
   try {
    const res = await api.get(`/api/posts/${post.id}`);
    selectedPost.value = res.data;
    await loadComments(post.id);
    // 부모에게도 알리고 싶으면 emit('open-detail', res.data)
  } catch (err) {
    alert('게시글을 불러오지 못했습니다.');
  }
};

const loadComments = async (postId) => {
  try {
    const res = await api.get(`/api/posts/${postId}/comments`);
    comments.value = res.data;
  } catch {
    comments.value = [];
  }
};

const submitComment = async () => {
  if (!selectedPost.value) return;
  if (!newComment.value.content.trim() || !newComment.value.password.trim()) {
    alert('댓글 내용과 비밀번호를 입력해 주세요.');
    return;
  }
  try {
    await api.post(`/api/posts/${selectedPost.value.id}/comments`, {
      content: newComment.value.content,
      password: newComment.value.password,
    });
    await loadComments(selectedPost.value.id);
    emit('refresh-posts');
    newComment.value = { content: '', password: '' };
  } catch (err) {
    alert(err?.response?.data?.detail || '댓글 등록에 실패했습니다.');
  }
};

const deleteComment = async (comment) => {
  const password = prompt('댓글 삭제 비밀번호를 입력하세요:');
  if (!password) return;
  try {
    await api.delete(`/api/posts/${selectedPost.value.id}/comments/${comment.id}`, { data: { password } });
    await loadComments(selectedPost.value.id);
    emit('refresh-posts');
  } catch (err) {
    alert(err?.response?.data?.detail || '댓글 삭제에 실패했습니다.');
  }
};

const likeSelected = async () => {
  if (!selectedPost.value) return;
  try {
    const res = await api.post(`/api/posts/${selectedPost.value.id}/like`);
    selectedPost.value = res.data;
    emit('refresh-posts');
  } catch {
    alert('좋아요 반영에 실패했습니다.');
  }
};

const verifyPassword = async () => {
  if (!selectedPost.value || !inputPwd.value.trim()) {
    alert('비밀번호를 입력해 주세요.');
    return;
  }
  try {
    if (pwdMode.value === 'delete') {
      await api.delete(`/api/posts/${selectedPost.value.id}`, { data: { password: inputPwd.value } });
      emit('refresh-posts');
      selectedPost.value = null;
    } else if (pwdMode.value === 'edit') {
      const newTitle = prompt('수정할 제목:', selectedPost.value.title);
      const newContent = prompt('수정할 내용:', selectedPost.value.content);
      if (!newTitle || !newContent) {
        pwdMode.value = null;
        return;
      }
      const res = await api.put(`/api/posts/${selectedPost.value.id}`, {
        password: inputPwd.value,
        category: selectedPost.value.category,
        title: newTitle,
        content: newContent
      });
      selectedPost.value = res.data;
      emit('refresh-posts');
      pwdMode.value = null;
    }
  } catch (err) {
    alert(err?.response?.data?.detail || '비밀번호가 일치하지 않거나 처리에 실패했습니다.');
  } finally {
    inputPwd.value = '';
  }
};
</script>