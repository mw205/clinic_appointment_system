<script setup>
const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
</script>

<template>
  <div class="max-w-3xl mx-auto p-6 flex flex-col gap-6">
    <h1 class="text-2xl font-bold">Doctor Schedule</h1>
    <div v-for="day in days" :key="day" class="p-4 border rounded shadow-sm bg-white">
      <p class="font-medium">{{ day }}</p>
    </div>
  </div>
</template>
