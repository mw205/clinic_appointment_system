<script setup>
import { computed, onMounted } from "vue";

import { useAuth } from "@/composables/useAuth.js";
import AppointmentsView from "../shared/AppointmentsView.vue";

const { user } = useAuth();

const doctorId = computed(() => user.value.profile_id);
const fixedParams = computed(() => {
  if (!doctorId.value) {
    return {};
  }

  return {
    status: "requested",
    doctor_id: doctorId.value,
  };
});

// onMounted(async () => {
//   if (!doctorId.value) {
//     await getCurrentUserProfile();
//   }
// });
</script>

<template>
  <AppointmentsView
    v-if="doctorId"
    mode="doctor"
    title="Pending Requests"
    fetch-mode="list"
    :fixed-params="fixedParams"
    :can-confirm="true"
    :show-tabs="false"
    :show-status-filter="false"
  />
</template>
