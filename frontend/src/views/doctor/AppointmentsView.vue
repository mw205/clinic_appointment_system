<script setup>
import { computed } from "vue";

import { useAuth } from "@/composables/useAuth.js";
import AppointmentsView from "../shared/AppointmentsView.vue";

const { user } = useAuth();

const doctorId = computed(() => user.value?.profile_id);
const fixedParams = computed(() => {
  if (!doctorId.value) {
    return {};
  }

  return {
    doctor_id: doctorId.value,
    ordering: "start_time,check_in_time",
  };
});
</script>

<template>
  <AppointmentsView
    v-if="doctorId"
    mode="doctor"
    title="All Appointments"
    fetch-mode="list"
    :fixed-params="fixedParams"
    :can-start-consultation="true"
    :can-view-record="true"
    :use-single-date-filter="true"
  />
</template>
