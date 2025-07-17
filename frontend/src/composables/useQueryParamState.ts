import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

/*
*  For using queryParams as state. It uses the standard
*  format of ?paramName=value and supports arrays too. Ex: 
*
*   URL:
*     ?filters=a&filters=b 
*   Code:
*     const selectedFilters = useQueryParamState('filters')
*     selectedFilters.value = ['a', 'b']
*/
export function useQueryParamState(paramName: string, defaultValue: string[] = []) {
  const route = useRoute();
  const router = useRouter();

  const param = computed({
    get() {
      const value = route.query[paramName];
      return Array.isArray(value) ? value : value ? [value] : [];
    },
    set(newValue: string[]) {
      router.replace({
        query: {
          ...route.query,
          [paramName]: newValue.length ? newValue : undefined
        }
      })
    }
  });

  // Initializes / auto-adds queryParams if passed in defaultValue 
  onMounted(() => {
    const hasParam = param.value.length > 0;

    if (!hasParam && defaultValue.length > 0) {
      param.value = defaultValue;
    }
  });

  return param;
}
