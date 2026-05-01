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
    status: "completed",
    ordering: "start_time,check_in_time",
  };
});
</script>

<template>
  <AppointmentsView
    v-if="doctorId"
    mode="doctor"
    title="Medical Records"
    fetch-mode="list"
    :fixed-params="fixedParams"
    :can-view-record="true"
    :show-tabs="false"
    :show-status-filter="false"
    :use-single-date-filter="true"
  />
</template>
