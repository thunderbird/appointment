<template>
  <!-- page title area -->
  <div class="flex flex-col lg:flex-row justify-end items-start select-none">
    <div
      class="flex flex-col gap-8 md:flex-row mx-auto lg:ml-0 lg:mr-0 items-center"
    >
      <button
        @click="selectDate(dj())"
        class="font-semibold text-base text-teal-500 px-4"
      >
        {{ t("label.today") }}
      </button>
      <tab-bar
        :tab-items="calendarViews"
        :active="tabActive"
        @update="updateTab"
        class="text-sm"
      />
    </div>
    <general-availability-page-heading
      :nav="true"
      :month="activeDate.format('MMMM')"
      :year="activeDate.year().toString()"
      :title="pageTitle"
      @prev="dateNav('auto', false)"
      @next="dateNav('auto')"
    />
  </div>
  <!-- page content -->
  <div
    class="flex flex-col flex-col-reverse md:flex-row justify-between gap-4 lg:gap-24 mt-8 items-stretch"
    :class="{ 'lg:mt-10': tabActive === calendarViews.month }"
  >
    <!-- page side bar -->
    <div class="w-full sm:w-1/2 md:w-1/5 mx-auto mb-10 md:mb-0 min-w-[310px]">
      <p>sidebar</p>
    </div>
    <!-- main section: big calendar showing active month, week or day -->
    <calendar-month
      v-show="tabActive === calendarViews.month"
      class="w-full md:w-4/5"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
    />
    <calendar-week
      v-show="tabActive === calendarViews.week"
      class="w-full md:w-4/5"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
    />
    <calendar-day
      v-show="tabActive === calendarViews.day"
      class="w-full md:w-4/5"
      :selected="activeDate"
      :appointments="pendingAppointments"
      :events="calendarEvents"
    />
  </div>
</template>

<script setup>
import { creationState, calendarViews, appointmentState } from "@/definitions";
import { ref, inject, computed, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
// import AppointmentCreation from "@/components/AppointmentCreation";
// import AppointmentListItem from "@/elements/AppointmentListItem";
import CalendarDay from "@/components/CalendarDay";
import CalendarMonth from "@/components/CalendarMonth";
import GeneralAvailabilityPageHeading from "@/elements/GeneralAvailabilityPageHeading";
import CalendarWeek from "@/components/CalendarWeek";
import PrimaryButton from "@/elements/PrimaryButton";
import TabBar from "@/components/TabBar";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const dj = inject("dayjs");
const call = inject("call");
const refresh = inject("refresh");

// view properties
const props = defineProps({
  calendars: Array, // list of calendars from db
  appointments: Array, // list of appointments from db
  user: Object, // currently logged in user, null if not logged in
});

// current selected date, if not in route: defaults to now
const activeDate = ref(route.params.date ? dj(route.params.date) : dj());
const selectDate = (d) => {
  router.replace({
    name: route.name,
    params: { view: route.params.view, date: dj(d).format("YYYY-MM-DD") },
  });
  activeDate.value = dj(d);
};

// date calculations
const startOfActiveWeek = computed(() => activeDate.value.startOf("week"));
const endOfActiveWeek = computed(() => activeDate.value.endOf("week"));

// active menu item for tab navigation of calendar views
const tabActive = ref(calendarViews[route.params.view] ?? calendarViews.month);
const updateTab = (view) => {
  router.replace({
    name: route.name,
    params: { view, date: route.params.date ?? dj().format("YYYY-MM-DD") },
  });
  tabActive.value = calendarViews[view];
};

// calculate page title
const pageTitle = computed(() => {
  switch (tabActive.value) {
    case calendarViews.day:
      return activeDate.value.format("dddd Do");
    case calendarViews.week:
      return `${startOfActiveWeek.value.format(
        "ddd Do"
      )} - ${endOfActiveWeek.value.format("ddd Do")}`;
    case calendarViews.month:
    default:
      return "";
  }
});

// date navigation
const dateNav = (unit = "auto", forward = true) => {
  if (unit === "auto") {
    unit = Object.keys(calendarViews).find(
      (key) => calendarViews[key] === tabActive.value
    );
  }
  if (forward) {
    selectDate(activeDate.value.add(1, unit));
  } else {
    selectDate(activeDate.value.subtract(1, unit));
  }
};

// appointment creation state
const creationStatus = ref(creationState.hidden);

// list of all pending appointments
const pendingAppointments = computed(() =>
  props.appointments?.filter((a) => a.status === appointmentState.pending)
);

// get remote calendar data for current year
const calendarEvents = ref([]);

const getRemoteEvents = async (from, to) => {
  calendarEvents.value = [];
  await Promise.all(
    props.calendars.map(async (calendar) => {
      const { data } = await call(`rmt/cal/${calendar.id}/${from}/${to}`)
        .get()
        .json();
      if (Array.isArray(data.value)) {
        calendarEvents.value.push(
          ...data.value.map((e) => ({
            ...e,
            duration: dj(e.end).diff(dj(e.start), "minutes"),
          }))
        );
      }
    })
  );
};

// initially load data when component gets remounted
onMounted(async () => {
  await refresh();
  const eventsFrom = dj(activeDate.value).startOf("year").format("YYYY-MM-DD");
  const eventsTo = dj(activeDate.value).endOf("year").format("YYYY-MM-DD");
  await getRemoteEvents(eventsFrom, eventsTo);
});

// react to user calendar navigation
watch(
  () => activeDate.value,
  (newValue, oldValue) => {
    // remote data is retrieved per year, so data request happens only if the user navigates to a different year
    if (dj(oldValue).format("YYYY") !== dj(newValue).format("YYYY")) {
      getRemoteEvents(
        dj(newValue).startOf("year").format("YYYY-MM-DD"),
        dj(newValue).endOf("year").format("YYYY-MM-DD")
      );
    }
  }
);
</script>
