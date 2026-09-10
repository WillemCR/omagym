export default async function* reporter(source) {
  for await (const event of source) {
    if (event.type === 'test:pass' || event.type === 'test:fail') {
      yield JSON.stringify({name: event.data.name, action: event.data.skip || event.data.todo ? 'skip' : event.type === 'test:pass' ? 'pass' : 'fail', detail: event.data.details?.error?.message || ''}) + '\n';
    } else if (event.type === 'test:stderr' || event.type === 'test:stdout') {
      yield JSON.stringify({output: event.data.message}) + '\n';
    }
  }
}
