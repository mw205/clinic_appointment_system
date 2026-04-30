<script setup>
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationFirst,
  PaginationItem,
  PaginationLast,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
  totalItems: {
    type: Number,
    default: 0,
  },
});

const emit = defineEmits(["change"]);
</script>

<template>
  <div v-if="totalPages > 1" class="flex flex-col items-center gap-3 pt-4">
    <Pagination
      :page="currentPage"
      :total="totalPages"
      :items-per-page="1"
      :sibling-count="1"
      show-edges
      @update:page="emit('change', $event)"
    >
      <PaginationContent v-slot="{ items }">
        <PaginationFirst />
        <PaginationPrevious />

        <template v-for="(item, index) in items" :key="`${item.type}-${item.value ?? index}`">
          <PaginationItem
            v-if="item.type === 'page'"
            :value="item.value"
            :is-active="item.value === currentPage"
          >
            {{ item.value }}
          </PaginationItem>

          <PaginationEllipsis
            v-else
            :index="index"
          />
        </template>

        <PaginationNext />
        <PaginationLast />
      </PaginationContent>
    </Pagination>

    <p class="text-sm text-muted-foreground">
      {{ totalItems }} appointments
    </p>
  </div>
</template>
