<template>
  <base-statistics-table
    v-model:expanded="expanded"
    class="component-statistics"
    :headers="headers"
    :items="items"
    :loading="loading"
    :mobile-breakpoint="1000"
    :total-columns="totalColumns"
    loading-text="Loading component statistics..."
    no-data-text="No component statistics available"
    item-value="component"
    show-expand
    return-object
    :necessary-total="true"
  >
    <template v-slot:expanded-row="{ item }">
      <tr>
        <expanded-item :item="item" :colspan="headers.length" />
      </tr>
    </template>

    <template
      v-for="(_, slot) of $slots"
      v-slot:[slot]="scope"
    >
      <slot :name="slot" v-bind="scope" />
    </template>
  </base-statistics-table>
</template>

<script setup>
import { ref, watch } from "vue";

import {
  BaseStatisticsTable,
  getCheckerStatistics
} from "@/components/Statistics";
import { ReportFilter } from "@cc/report-server-types";
import ExpandedItem from "./ExpandedItem";

const props = defineProps({
  items: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  totalColumns: { type: Array, default: undefined },
  filters: { type: Object, default: () => {} }
});

const expanded = ref([]);

const headers = [
  {
    text: "",
    key: "data-table-expand"
  },
  {
    text: "Component",
    key: "component",
    align: "center"
  },
  {
    text: "Unreviewed",
    key: "unreviewed.count",
    align: "center"
  },
  {
    text: "Confirmed bug",
    key: "confirmed.count",
    align: "center"
  },
  {
    text: "Outstanding reports",
    key: "outstanding.count",
    align: "center"
  },
  {
    text: "False positive",
    key: "falsePositive.count",
    align: "center"
  },
  {
    text: "Intentional",
    key: "intentional.count",
    align: "center"
  },
  {
    text: "Suppressed reports",
    key: "suppressed.count",
    align: "center"
  },
  {
    text: "All reports",
    key: "reports.count",
    align: "center"
  }
];

watch(expanded, function(newVal, oldVal) {
  const added = newVal.find(_item => !oldVal.includes(_item));
  if (added) {
    loadCheckerStatistics(added);
  }
});

watch(function() { return props.loading; }, function() {
  if (props.loading) return;

  expanded.value.forEach(_e => {
    const _item = props.items.find(_i => _i.component === _e.component);
    if (_item) loadCheckerStatistics(_item);
  });
});

async function loadCheckerStatistics(item) {
  if (!item || item.checkerStatistics) return;

  item.loading = true;

  const _component = item.component;
  const _runIds = props.filters.runIds;
  const _reportFilter = new ReportFilter(props.filters.reportFilter);
  _reportFilter["componentNames"] = [ _component ];
  const _cmpData = props.filters.cmpData;

  const _stats = await getCheckerStatistics(_runIds, _reportFilter, _cmpData);
  item.checkerStatistics = _stats.map(_stat => ({
    ..._stat,
    $queryParams: { "source-component": _component }
  }));
  item.loading = false;
}
</script>

<style lang="scss">
@use "@/components/Statistics/colored-columns" with (
  $class-name: ".component-statistics"
);
</style>
