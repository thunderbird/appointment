// get the first key of given object that points to given value
export const keyByValue = (o, v) => Object.keys(o).find(k => o[k]===v);

export default {
	keyByValue
}
