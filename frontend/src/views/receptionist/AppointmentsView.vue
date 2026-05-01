<script setup>
import AppointmentsView from "../shared/AppointmentsView.vue";

const fixedParams = {
  ordering: "start_time,check_in_time",
};
</script>

<template>
  <AppointmentsView
    mode="receptionist"
    title="All Appointments"
    fetch-mode="list"
    :fixed-params="fixedParams"
    :can-confirm="true"
    :can-view-record="true"
    :use-single-date-filter="true"
  />
</template>
