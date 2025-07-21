import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

/*
*  For using queryParams as state. It uses the standard
*  format of ?paramName=value and supports arrays too. Ex: 
*
*   URL:
*     ?filters=a&filters=b 
*   Code:
*     const selectedFilters = useQueryParamState('filters', ['pending', 'confirmed'])
*     selectedFilters.value = ['pending', 'confirmed']
*
*/

type QueryPrimitive = string | number | boolean;
type QueryValue = QueryPrimitive | QueryPrimitive[];

export function useQueryParamState<T extends QueryValue>(
  paramName: string,
  defaultValue: T
) {
  const route = useRoute();
  const router = useRouter();

  const isArray = Array.isArray(defaultValue);

  function parseValue(v: string): QueryPrimitive {
    if (typeof defaultValue === 'boolean') {
      return v === 'true';
    }

    if (typeof defaultValue === 'number' || (isArray && typeof defaultValue[0] === 'number')) {
      const num = Number(v);
      return isNaN(num) ? 0 : num;
    }

    return v;
  }

  const param = computed<T>({
    get() {
      const raw = route.query[paramName];

      if (isArray) {
        const rawArray = Array.isArray(raw) ? raw : raw ? [raw] : [];
        return rawArray.map((v) => parseValue(v)) as T;
      } else {
        const single = Array.isArray(raw) ? raw[0] : raw;
        return single !== undefined ? (parseValue(single) as T) : defaultValue;
      }
    },
    set(newValue: T) {
      const stringify = (v: QueryPrimitive) => String(v);

      const value = isArray
        ? (newValue as QueryPrimitive[]).length
          ? (newValue as QueryPrimitive[]).map(stringify)
          : undefined
        : newValue !== undefined && newValue !== null
          ? stringify(newValue as QueryPrimitive)
          : undefined;

      router.replace({
        query: {
          ...route.query,
          [paramName]: value,
        },
      });
    },
  });

  onMounted(() => {
    const current = param.value;

    if (
      (isArray && (current as QueryPrimitive[]).length === 0) ||
      (!isArray && current === undefined)
    ) {
      param.value = defaultValue;
    }
  });

  return param;
}
