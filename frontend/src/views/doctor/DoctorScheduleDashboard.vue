<script setup>

</script>
<template>

  <div class="max-w-3xl mx-auto p-6 flex flex-col gap-6">
    <div v-bind:v-for="day in day_week">
      <p>{{ day }}</p>
    </div>
  </div>
</template>
