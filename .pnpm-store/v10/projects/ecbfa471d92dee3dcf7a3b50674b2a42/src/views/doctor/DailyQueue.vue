<script setup>
import { computed } from "vue";

import { useAuth } from "@/composables/useAuth.js";
import AppointmentsView from "../shared/AppointmentsView.vue";

const { user } = useAuth();

const today = new Date().toLocaleDateString('en-CA')
const doctorId = computed(() => user.value?.profile_id);
const fixedParams = computed(() => {
  if (!doctorId.value) {
    return {
      date: today,
      ordering: "start_time,check_in_time",
    };
  }

  return {
    doctor_id: doctorId.value,
    date: today,
    ordering: "start_time,check_in_time",
  };
});
</script>

<template>
  <AppointmentsView
    v-if="doctorId"
    mode="doctor"
    title="Today's Schedule"
    fetch-mode="list"
    :fixed-params="fixedParams"
    :can-start-consultation="true"
    :use-time-range-filters="true"
  />
</template>
