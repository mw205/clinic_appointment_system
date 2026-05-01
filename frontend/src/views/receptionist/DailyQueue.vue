<script setup>
import AppointmentsView from "../shared/AppointmentsView.vue";

const today = new Date().toLocaleDateString('en-CA')
const fixedParams = {
  date: today,
  ordering: "start_time,check_in_time",
}
</script>

<template>
  <AppointmentsView
    mode="receptionist"
    title="Today's Schedule"
    fetch-mode="list"
    :fixed-params="fixedParams"
    :can-confirm="true"
    :use-time-range-filters="true"
    :can-view-record="true"
  />
</template>
