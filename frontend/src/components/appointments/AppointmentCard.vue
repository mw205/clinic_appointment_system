<script setup>
import { computed } from "vue";
import { Badge } from "@/components/ui/badge/index.ts";
import { Button } from "@/components/ui/button/index.ts";
import { Clock, UserCheck, Users } from "lucide-vue-next";
import { useFormatters } from "@/composables/useFormatters.js";

const props = defineProps({
  appointment: {
    type: Object,
    required: true,
  },
  calculateWaitTime: {
    type: Function,
    required: true,
  },
});

const emit = defineEmits(["check-in", "no-show", "complete", "view-record"]);

const { formatTime } = useFormatters();

const waitTime = computed(() => props.calculateWaitTime(props.appointment.check_in_time));
</script>

<template>
  <div class="p-4 rounded-lg border border-gray-200 hover:shadow-md transition-all">
    <div class="flex items-start justify-between gap-4">
      <div class="flex items-start gap-4 flex-1">
        <div class="p-2 bg-blue-100 rounded-lg">
          <Users class="w-5 h-5 text-blue-600" />
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-3">
            <p class="font-medium text-gray-900">{{ appointment.patient.user.username }}</p>
            <Badge variant="secondary">
              {{ appointment.status }}
              <span v-if="appointment.status === 'checked_in'">
                {{ formatTime(appointment.check_in_time) }}
              </span>
            </Badge>
            <Badge
              v-if="appointment.check_in_time && appointment.status !== 'no_show'"
              variant="outline"
              class="text-orange-600"
            >
              Waiting {{ waitTime }} min
            </Badge>
          </div>
          <div class="flex items-center gap-4 mt-2 text-sm text-gray-600">
            <span class="flex items-center gap-1">
              <Clock class="w-4 h-4" />
              {{ formatTime(appointment.start_time) }} - {{ formatTime(appointment.end_time) }}
            </span>
          </div>
        </div>
      </div>

      <div class="flex gap-2 flex-shrink-0">
        <Button
          v-if="appointment.status === 'confirmed'"
          size="sm"
          variant="outline"
          @click="emit('check-in', appointment.id)"
        >
          <UserCheck class="w-4 h-4 mr-1" /> Check In
        </Button>

        <Button
          v-if="appointment.status !== 'completed' && appointment.status !== 'no_show'"
          size="sm"
          variant="outline"
          @click="emit('no-show', appointment.id)"
        >
          No Show
        </Button>

        <Button
          v-if="appointment.status === 'checked_in'"
          size="sm"
          class="bg-green-600 hover:bg-green-700"
          @click="emit('complete', appointment.id)"
        >
          Start Consultation
        </Button>

        <Button
          v-if="appointment.status === 'completed'"
          size="sm"
          variant="outline"
          @click="emit('view-record', appointment.id)"
        >
          View Record
        </Button>
      </div>
    </div>
  </div>
</template>
