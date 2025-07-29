import { defineStore } from 'pinia';
import { ref, computed, inject } from 'vue';
import { BookingStatus, MetricEvents } from '@/definitions';
import { useUserStore } from '@/stores/user-store';
import {
  Appointment, AppointmentListResponse, Fetch, Slot,
  AvailabilitySlotResponse, PendingAppointmentsCount, PageMeta
} from '@/models';
import { dayjsKey, tzGuessKey } from '@/keys';
import { usePosthog, posthog } from '@/composables/posthog';
import { FILTER_QUERY_PARAM_TO_BOOKING_STATUS } from '@/views/BookingsView/constants';

export const useAppointmentStore = defineStore('appointments', () => {
  const dj = inject(dayjsKey);
  const tzGuess = inject(tzGuessKey);
  const call = ref(null);

  // State
  const isLoaded = ref(false);
  const isLoading = ref(false);
  const hasMorePages = ref(true);
  const currentPage = ref(1);
  const pageMeta = ref<PageMeta | null>(null);

  // Data
  const appointments = ref<Appointment[]>([]);
  const pendingAppointments = computed(
    (): Appointment[] => appointments.value.filter((a) => a?.slots[0]?.booking_status === BookingStatus.Requested),
  );
  const pendingFutureAppointments = computed(
    (): Appointment[] => pendingAppointments.value.filter((a) => a?.slots[0]?.start > dj()),
  );
  const selectedAppointment = ref<Appointment | null>(null);

  /**
   * Initialize store with data required at runtime
   *
   * @param fetch preconfigured function to perform API calls
   */
  const init = (fetch: Fetch) => {
    call.value = fetch;
  }

  /**
   * Append additional data to retrieved appointments
   */
  const postFetchProcess = async (newAppointments: Appointment[]) => {
    const userStore = useUserStore();

    newAppointments.forEach((a) => {
      a.active = a.status !== BookingStatus.Booked;
      // convert start dates from UTC back to users timezone
      a.slots.forEach((s: Slot) => {
        s.start = dj(s.start).utc(true).tz(userStore.data.settings.timezone ?? tzGuess);
      });
    });

    // Update selectedAppointment with the latest data
    if (selectedAppointment.value) {
      const appointment = appointments.value.find((a) => a.id === selectedAppointment.value.id);
      selectedAppointment.value = appointment ?? null;
    }
  };

  /**
   * Convert filter query params to backend status values
   */
  const convertFiltersToStatusParams = (filters: string[]): string[] => {
    return filters.map(filter => {
      const status = FILTER_QUERY_PARAM_TO_BOOKING_STATUS[filter];
      return status ? BookingStatus[status].toLowerCase() : null;
    }).filter(Boolean);
  };

  /**
   * Get appointments for current user with pagination and filters
   */
  const fetch = async (page: number = 1, statusFilters: string[] = [], append: boolean = false) => {
    if (isLoading.value) return;

    isLoading.value = true;

    try {
      // Convert filter query params to backend status values
      const statusParams = convertFiltersToStatusParams(statusFilters);

      // Build query parameters
      const queryParams = new URLSearchParams({
        page: page.toString(),
        per_page: '50' // Default page size
      });

      // Add status filters if provided
      statusParams.forEach(status => {
        queryParams.append('status', status);
      });

      const { data, error }: AppointmentListResponse = await call.value(`me/appointments?${queryParams.toString()}`).get().json();

      if (!error.value && data.value) {
        const newAppointments = data.value.items;

        // Process the new appointments
        await postFetchProcess(newAppointments);

        if (append) {
          // Append to existing appointments
          appointments.value = [...appointments.value, ...newAppointments];
        } else {
          // Replace existing appointments
          appointments.value = newAppointments;
        }

        // Update pagination state
        pageMeta.value = data.value.page_meta;
        currentPage.value = page;
        hasMorePages.value = page < data.value.page_meta.total_pages;
        isLoaded.value = true;
      }
    } finally {
      isLoading.value = false;
    }
  };

  /**
   * Load more appointments (for infinite scrolling)
   */
  const loadMore = async (statusFilters: string[] = []) => {
    if (!hasMorePages.value || isLoading.value) return;

    const nextPage = currentPage.value + 1;
    await fetch(nextPage, statusFilters, true);
  };

  /**
   * Refresh appointments (reset pagination and reload from page 1)
   */
  const refresh = async (statusFilters: string[] = []) => {
    currentPage.value = 1;
    hasMorePages.value = true;

    await fetch(1, statusFilters, false);
  };

  const fetchPendingAppointmentsCount = async () => {
    const { data, error }: PendingAppointmentsCount = await call.value('me/appointments_count_by_status?status=requested').get().json();
    return { data, error };
  }

  /**
   * Restore default state, empty and unload appointments
   */
  const $reset = () => {
    appointments.value = [];
    isLoaded.value = false;
    isLoading.value = false;
    hasMorePages.value = true;
    currentPage.value = 1;
    pageMeta.value = null;
  };

  /**
   * Remove an appointment and all assigned time slots
   */
  const deleteAppointment = async (id: number) => {
    await call.value(`apmt/${id}`).delete();
    await refresh();
  };

  /**
   * Confirm or deny a booking slot
   */
  const confirmOrDenyBooking = async ({ slotId, slotToken, ownerUrl, confirmed }) => {
    const obj = {
      slot_id: slotId,
      slot_token: slotToken,
      owner_url: ownerUrl,
      confirmed,
    };
    const { error, data }: AvailabilitySlotResponse = await call.value('schedule/public/availability/booking').put(obj).json();

    if (usePosthog && !error.value) {
      const event = confirmed ? MetricEvents.ConfirmBooking : MetricEvents.DenyBooking;
      posthog.capture(event);
    }

    await refresh();

    return { error, data };
  };

  /**
   * Cancel an appointment (booking context)
   */
  const cancelAppointment = async (appointmentId: number) => {
    const { error } = await call.value(`apmt/${appointmentId}/cancel`).post().json();

    if (usePosthog && !error.value) {
      posthog.capture(MetricEvents.CancelBooking);
    }

    await refresh();

    return { error };
  };

  /**
   * Modify an appointment (booking context)
   */
  const modifyBookingAppointment = async ({ appointmentId, title, start, slotId, notes }) => {
    const payload = { title, start, slot_id: slotId, notes };

    const { error } = await call.value(`apmt/${appointmentId}/modify`).put(payload).json();

    if (usePosthog && !error.value) {
      posthog.capture(MetricEvents.ModifyBooking);
    }

    await refresh();

    return { error };
  };

  /**
   * Fetch available slots for a given day
   */
  const fetchAvailabilityForDay = async (date: string) => {
    const { data, error } = await call.value(`/schedule/availability_for_day?date=${date}`).get().json();
    return { data, error };
  };

  return {
    isLoaded,
    isLoading,
    hasMorePages,
    currentPage,
    pageMeta,
    appointments,
    selectedAppointment,
    pendingAppointments,
    pendingFutureAppointments,
    init,
    postFetchProcess,
    fetch,
    loadMore,
    refresh,
    $reset,
    deleteAppointment,
    cancelAppointment,
    confirmOrDenyBooking,
    modifyBookingAppointment,
    fetchAvailabilityForDay,
    fetchPendingAppointmentsCount,
  };
});

export const createAppointmentStore = (call: Fetch) => {
  const store = useAppointmentStore();
  store.init(call);
  return store;
};
