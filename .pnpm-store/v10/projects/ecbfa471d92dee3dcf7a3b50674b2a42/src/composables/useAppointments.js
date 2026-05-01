import { computed, ref } from "vue";

export function useAppointments(dailyQueue, options = {}) {
  const { includeDoctorNameFilter = false, useTimeRangeFilters = false, baseDate = "" } = options;

  const filters = ref({
    status: "all",
    patientName: "",
    doctorName: "",
    startDate: "",
    endDate: "",
  });

  const stats = computed(() => ({
    total: dailyQueue.value.length,
    confirmed: dailyQueue.value.filter((appointment) => appointment.status === "confirmed").length,
    checkedIn: dailyQueue.value.filter((appointment) => appointment.status === "checked_in").length,
    completed: dailyQueue.value.filter((appointment) => appointment.status === "completed").length,
    hidden: dailyQueue.value.filter((appointment) => appointment.status === "no_show").length,
  }));

  const appointmentsByTab = computed(() => ({
    all: dailyQueue.value.filter((appointment) => appointment.status !== "no_show"),
    checked_in: dailyQueue.value.filter((appointment) => appointment.status === "checked_in"),
    no_show: dailyQueue.value.filter((appointment) => appointment.status === "no_show"),
  }));

  const hasActiveFilters = computed(() =>
    filters.value.status !== "all"
    || filters.value.patientName.trim() !== ""
    || (includeDoctorNameFilter && filters.value.doctorName.trim() !== "")
    || filters.value.startDate !== ""
    || filters.value.endDate !== "",
  );

  const requestParams = computed(() => {
    const params = {};
    const effectiveBaseDate = baseDate || new Date().toISOString().slice(0, 10);

    if (filters.value.status !== "all") {
      params.status = filters.value.status;
    }

    if (filters.value.patientName.trim()) {
      params.patient_name = filters.value.patientName.trim();
    }

    if (includeDoctorNameFilter && filters.value.doctorName.trim()) {
      params.doctor_name = filters.value.doctorName.trim();
    }

    if (filters.value.startDate) {
      params.start_from = useTimeRangeFilters
        ? `${effectiveBaseDate}T${filters.value.startDate}:00`
        : `${filters.value.startDate}T00:00:00`;
    }

    if (filters.value.endDate) {
      params.start_to = useTimeRangeFilters
        ? `${effectiveBaseDate}T${filters.value.endDate}:59`
        : `${filters.value.endDate}T23:59:59`;
    }

    return params;
  });

  function resetFilters() {
    filters.value = {
      status: "all",
      patientName: "",
      doctorName: "",
      startDate: "",
      endDate: "",
    };
  }

  function calculateWaitTime(checkInTime) {
    if (!checkInTime) {
      return null;
    }

    const now = new Date();
    const checkedIn = new Date(checkInTime);
    const diffMs = now.getTime() - checkedIn.getTime();

    return Math.floor(diffMs / 60000);
  }

  return {
    filters,
    stats,
    appointmentsByTab,
    hasActiveFilters,
    requestParams,
    resetFilters,
    calculateWaitTime,
  };
}
