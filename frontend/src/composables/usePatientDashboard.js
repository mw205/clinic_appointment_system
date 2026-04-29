import { computed, ref } from "vue";
import { getApiErrorMessage, getAppointments } from "@/services/appointmentService";

export function usePatientDashboard() {
  const appointments = ref([]);
  const loading = ref(true);
  const errorMessage = ref("");

  const upcomingAppointments = computed(() =>
    appointments.value.filter((appointment) =>
      ["requested", "confirmed", "checked_in"].includes(appointment.status)
      && new Date(appointment.start_time) >= new Date()
    )
  );

  const completedAppointments = computed(() =>
    appointments.value.filter((appointment) => appointment.status === "completed")
  );

  const nextAppointment = computed(() => {
    return [...upcomingAppointments.value].sort(
      (a, b) => new Date(a.start_time) - new Date(b.start_time)
    )[0];
  });

  async function loadAppointments() {
    loading.value = true;
    errorMessage.value = "";

    try {
      const data = await getAppointments({
        ordering: "start_time",
        page_size: 10,
      });

      appointments.value = data.results ?? data;
    } catch (error) {
      errorMessage.value = getApiErrorMessage(error, "Unable to load appointments.");
    } finally {
      loading.value = false;
    }
  }

  function formatDateTime(value) {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  }

  function statusVariant(status) {
    const variants = {
      confirmed: "default",
      completed: "secondary",
      cancelled: "destructive",
      no_show: "destructive",
      requested: "outline",
      checked_in: "secondary",
    };

    return variants[status] ?? "outline";
  }

  return {
    appointments,
    loading,
    errorMessage,
    upcomingAppointments,
    completedAppointments,
    nextAppointment,
    loadAppointments,
    formatDateTime,
    statusVariant,
  };
}
