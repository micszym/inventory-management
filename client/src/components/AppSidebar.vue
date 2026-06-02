<template>
  <aside class="sidebar">
    <!-- Brand -->
    <div class="sidebar-brand">
      <span class="brand-name">{{ t('nav.companyName') }}</span>
      <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
    </div>

    <!-- Nav -->
    <nav class="sidebar-nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <span class="nav-icon" v-html="getIcon(item.icon)"></span>
        <span>{{ item.label() }}</span>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script>
import { useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

const icons = {
  grid: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
  layers: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 7H4a2 2 0 00-2 2v6a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/></svg>',
  'check-square': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>',
  dollar: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>',
  activity: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
  package: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>',
  'file-text': '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
}

export default {
  name: 'AppSidebar',

  components: {
    LanguageSwitcher,
    ProfileMenu,
  },

  emits: ['show-profile-details', 'show-tasks'],

  setup() {
    const route = useRoute()
    const { t } = useI18n()

    const isActive = (path) => {
      if (path === '/') return route.path === '/'
      return route.path.startsWith(path)
    }

    const navItems = [
      { path: '/',           label: () => t('nav.overview'),       icon: 'grid' },
      { path: '/inventory',  label: () => t('nav.inventory'),      icon: 'layers' },
      { path: '/orders',     label: () => t('nav.orders'),         icon: 'check-square' },
      { path: '/spending',   label: () => t('nav.finance'),        icon: 'dollar' },
      { path: '/demand',     label: () => t('nav.demandForecast'), icon: 'activity' },
      { path: '/restocking', label: () => t('nav.restocking'),     icon: 'package' },
      { path: '/reports',    label: () => 'Reports',               icon: 'file-text' },
    ]

    const getIcon = (name) => icons[name] || ''

    return { t, navItems, isActive, getIcon }
  },
}
</script>

<style scoped>
.sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-brand {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  flex-shrink: 0;
}

.brand-name {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.015em;
}

.brand-subtitle {
  display: block;
  font-size: 0.75rem;
  color: #475569;
  margin-top: 0.125rem;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;
  cursor: pointer;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #f1f5f9;
}

.nav-item.active {
  background: rgba(37, 99, 235, 0.25);
  color: #60a5fa;
  font-weight: 600;
}

.nav-icon {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  opacity: 0.85;
}

.nav-item.active .nav-icon {
  opacity: 1;
}

/* ── Sidebar footer ───────────────────────────────────────────────── */

.sidebar-footer {
  padding: 0.75rem;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-shrink: 0;
}

/* Dark-adapt LanguageSwitcher button for the dark sidebar */
.sidebar-footer :deep(.language-button) {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.12);
  color: #94a3b8;
  padding: 0.4rem 0.625rem;
  font-size: 0.8rem;
}

.sidebar-footer :deep(.language-button):hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
  color: #f1f5f9;
}

.sidebar-footer :deep(.language-button .globe-icon) {
  color: #64748b;
}

.sidebar-footer :deep(.language-button):hover .globe-icon {
  color: #94a3b8;
}

/* Dark-adapt ProfileMenu button for the dark sidebar */
.sidebar-footer :deep(.profile-button) {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.12);
  color: #94a3b8;
  padding: 0.4rem 0.625rem;
}

.sidebar-footer :deep(.profile-button):hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.2);
}

.sidebar-footer :deep(.profile-name) {
  color: #94a3b8;
  font-size: 0.8rem;
}

.sidebar-footer :deep(.profile-button):hover .profile-name {
  color: #f1f5f9;
}

.sidebar-footer :deep(.chevron) {
  color: #475569;
}

/* Open dropdowns UPWARD since the footer is at the bottom of the screen */
.sidebar-footer :deep(.dropdown-menu) {
  top: auto !important;
  bottom: calc(100% + 0.5rem);
  right: 0;
  left: auto;
}

/* Scrollbar styling for nav */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>
