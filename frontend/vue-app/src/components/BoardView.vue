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
    <div class="flex flex-col sm:flex-row justify-between gap-3 bg-white/40 p-3 rounded-2xl border border-white">
      <div class="flex flex-wrap gap-1.5">
        <button v-for="cat in categories" :key="cat" @click="selectedCategory = cat" :class="selectedCategory === cat ? 'bg-cerulean-700 text-white font-bold' : 'bg-white/80 text-slate-600 hover:bg-white'" class="px-3 py-1.5 rounded-lg text-xs transition shadow-sm">
          {{ getCategoryIcon(cat) }} {{ cat }}
        </button>
      </div>
      <div class="relative min-w-[220px]">
        <input v-model="searchKeyword" type="text" placeholder="🔍 제목, 내용 검색..." class="w-full bg-white/90 border border-slate-200 rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-cerulean-500">
      </div>
    </div>

    <!-- 게시글 목록 테이블 -->
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-slate-200/80 text-slate-400 text-xs uppercase">
            <th class="py-3 px-2 font-medium w-16">번호</th>
            <th class="py-3 px-2 font-medium w-24">분류</th>
            <th class="py-3 px-2 font-medium">제목</th>
            <th class="py-3 px-2 font-medium w-20 text-center">조회</th>
            <th class="py-3 px-2 font-medium w-20 text-center">좋아요</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 text-sm">
          <tr v-for="post in filteredPosts" :key="post.id" @click="openDetail(post)" class="hover:bg-white/60 transition cursor-pointer">
            <td class="py-3 px-2 text-slate-400 text-xs">{{ post.id }}</td>
            <td class="py-3 px-2"><span class="bg-cerulean-50 text-cerulean-700 text-[11px] font-semibold px-2 py-0.5 rounded-md border border-cerulean-100">{{ getCategoryIcon(post.category) }} {{ post.category }}</span></td>
            <td class="py-3 px-2 font-medium text-slate-700 hover:text-cerulean-700 transition">{{ post.title }}</td>
            <td class="py-3 px-2 text-center text-xs text-slate-500">{{ post.views }}</td>
            <td class="py-3 px-2 text-center text-xs text-pink-500 font-semibold">❤️ {{ post.likes }}</td>
          </tr>
          <tr v-if="filteredPosts.length === 0">
            <td colspan="5" class="py-12 text-center text-slate-400 text-sm">등록된 게시글이 없습니다. 첫 글의 주인공이 되어보세요! ✨</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 모달 1: 게시글 작성 창 -->
    <div v-if="showWriteModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fade-in">
      <div class="glass-modal w-full max-w-lg rounded-3xl p-6 shadow-2xl border border-white space-y-4">
        <h3 class="text-lg font-bold text-cerulean-900 flex items-center">✨ 익명 게시글 작성</h3>
        <div class="space-y-3 text-sm">
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">카테고리</label>
            <select v-model="newPost.category" class="w-full bg-white/90 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-cerulean-500 outline-none">
              <option v-for="cat in categories.slice(1)" :key="cat" :value="cat">{{ getCategoryIcon(cat) }} {{ cat }}</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">제목</label>
            <input v-model="newPost.title" type="text" placeholder="제목을 입력하세요" class="w-full bg-white/90 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-cerulean-500 outline-none">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1">내용</label>
            <textarea v-model="newPost.content" rows="4" placeholder="자유롭게 지역 정보를 나누어 보세요!" class="w-full bg-white/90 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-cerulean-500 outline-none"></textarea>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-600 mb-1 text-rose-600">수정/삭제용 비밀번호 (평문 저장)</label>
            <input v-model="newPost.password" type="password" placeholder="숫자 4자리 등 기억할 비밀번호" class="w-full bg-white/90 border border-slate-200 rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-cerulean-500 outline-none">
          </div>
        </div>
        <div class="flex justify-end space-x-2 pt-2">
          <button @click="showWriteModal = false" class="px-4 py-2 rounded-xl bg-slate-200/80 text-slate-600 font-medium text-xs hover:bg-slate-300 transition">취소</button>
          <button @click="submitPost" class="px-5 py-2 rounded-xl bg-cerulean-700 text-white font-medium text-xs hover:bg-cerulean-800 transition shadow">등록하기</button>
        </div>
      </div>
    </div>

    <!-- 모달 2: 게시글 상세 & 비밀번호 확인 창 -->
    <div v-if="selectedPost" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
      <div class="glass-modal w-full max-w-lg rounded-3xl p-6 shadow-2xl border border-white space-y-4">
        <div class="flex justify-between items-start">
          <span class="bg-cerulean-100 text-cerulean-800 text-xs font-semibold px-2.5 py-1 rounded-md">{{ getCategoryIcon(selectedPost.category) }} {{ selectedPost.category }}</span>
          <button @click="selectedPost = null; pwdMode = null" class="text-slate-400 hover:text-slate-600 font-bold text-lg">✕</button>
        </div>
        <h3 class="text-xl font-bold text-slate-800">{{ selectedPost.title }}</h3>
        <p class="text-sm text-slate-600 min-h-[5rem] bg-white/60 p-4 rounded-2xl whitespace-pre-wrap border border-white">{{ selectedPost.content }}</p>
        
        <div class="flex justify-between items-center text-xs text-slate-400 pt-2 border-t border-slate-200/60">
          <span>👁️ 조회수 {{ selectedPost.views }}</span>
          <button @click="selectedPost.likes++" class="px-3 py-1.5 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-600 font-bold transition flex items-center space-x-1">
            <span>❤️ 좋아요 {{ selectedPost.likes }}</span>
          </button>
        </div>

        <div v-if="!pwdMode" class="flex justify-end space-x-2 pt-2">
          <button @click="pwdMode = 'edit'" class="px-3 py-1.5 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-medium transition">✏️ 수정</button>
          <button @click="pwdMode = 'delete'" class="px-3 py-1.5 bg-rose-500 hover:bg-rose-600 text-white rounded-xl text-xs font-medium transition">🗑️ 삭제</button>
        </div>

        <div v-else class="bg-cerulean-50/80 p-3 rounded-2xl border border-cerulean-200 space-y-2">
          <p class="text-xs font-bold text-cerulean-900">🔒 {{ pwdMode === 'edit' ? '수정' : '삭제' }} 권한 확인</p>
          <div class="flex space-x-2">
            <input v-model="inputPwd" type="password" placeholder="비밀번호 입력" class="flex-1 bg-white border border-slate-300 rounded-xl px-3 py-1.5 text-xs outline-none">
            <button @click="verifyPassword" class="px-4 py-1.5 bg-cerulean-700 text-white rounded-xl text-xs font-bold shadow hover:bg-cerulean-800">확인</button>
            <button @click="pwdMode = null; inputPwd = ''" class="px-3 py-1.5 bg-slate-300 text-slate-700 rounded-xl text-xs">취소</button>
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