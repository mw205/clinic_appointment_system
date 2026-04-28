import { computed } from "vue";

export function useAppointments(dailyQueue) {
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
    stats,
    appointmentsByTab,
    calculateWaitTime,
  };
}
