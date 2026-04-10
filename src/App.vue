<template>
  <RouterView />
</template>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  background: #0D0F14;
  color: #E8E0D0;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
}
a { color: inherit; text-decoration: none; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #1a1d24; }
::-webkit-scrollbar-thumb { background: #C9A84C; border-radius: 3px; }
</style>
